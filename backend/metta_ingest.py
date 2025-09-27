#!/usr/bin/env python3
"""
Dr.Doc MeTTa Knowledge Base

Clean MeTTa integration for symbolic reasoning and knowledge graph creation.
Extracts structured facts from documentation and converts them to MeTTa atoms.

Author: Dr.Doc Team
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import markdown
from bs4 import BeautifulSoup
from hyperon import MeTTa, Atom, E, S, V, G, OperationAtom, ValueAtom
from hyperon.atoms import GroundedAtom

class MeTTaFactExtractor:
    """Extracts structured facts from API documentation for MeTTa."""
    
    def __init__(self):
        self.atoms = []
        self.endpoints = set()
        self.error_codes = {}
        self.rate_limits = {}
        self.parameters = {}
        self.patterns = {}
        self.security_flows = {}
        self.performance_patterns = {}
        self.monitoring_concepts = {}
    
    def extract_endpoints(self, content: str, file_path: str) -> List[Atom]:
        """Extract API endpoints from documentation."""
        atoms = []
        
        # Pattern for HTTP methods and endpoints
        endpoint_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-{}]+)'
        matches = re.finditer(endpoint_pattern, content, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            endpoint = match.group(2).strip()
            
            # Clean up endpoint (remove parameters in curly braces for now)
            clean_endpoint = re.sub(r'\{[^}]+\}', '', endpoint)
            if clean_endpoint.endswith('/'):
                clean_endpoint = clean_endpoint[:-1]
            
            self.endpoints.add(clean_endpoint)
            
            # Create MeTTa atoms
            atoms.append(E(S('endpoint'), S(clean_endpoint)))
            atoms.append(E(S('method'), S(clean_endpoint), S(method)))
            atoms.append(E(S('file'), S(clean_endpoint), S(file_path)))
        
        return atoms
    
    def extract_parameters(self, content: str, file_path: str) -> List[Atom]:
        """Extract parameters from endpoint documentation."""
        atoms = []
        
        # Pattern for parameter definitions
        param_patterns = [
            r'`(\w+)`\s*\([^)]*\):\s*([^.\n]+)',
            r'(\w+)\s*\([^)]*\):\s*([^.\n]+)',
            r'`(\w+)`\s*\([^)]*\)\s*-\s*([^.\n]+)',
        ]
        
        for pattern in param_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                param_name = match.group(1).strip()
                param_desc = match.group(2).strip()
                
                # Try to find which endpoint this parameter belongs to
                endpoint = self._find_associated_endpoint(content, match.start())
                
                if endpoint:
                    atoms.append(E(S('param'), S(endpoint), S(param_name), S(param_desc)))
                    atoms.append(E(S('param-type'), S(endpoint), S(param_name), S('string')))  # Default type
        
        return atoms
    
    def extract_security_patterns(self, content: str, file_path: str) -> List[Atom]:
        """Extract security patterns and authentication flows."""
        atoms = []
        
        # OAuth patterns
        oauth_patterns = [
            r'OAuth 2\.0.*PKCE',
            r'authorization.*code.*flow',
            r'token.*refresh.*pattern',
            r'client.*credentials.*flow'
        ]
        
        for pattern in oauth_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                flow_type = match.group(0).lower()
                atoms.append(E(S('security_flow'), S(flow_type), S('oauth2')))
                atoms.append(E(S('file'), S(flow_type), S(file_path)))
        
        # Authentication methods
        auth_methods = [
            r'API.*key.*management',
            r'bearer.*token',
            r'JWT.*token',
            r'signature.*verification'
        ]
        
        for pattern in auth_methods:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                method = match.group(0).lower()
                atoms.append(E(S('auth_method'), S(method)))
                atoms.append(E(S('file'), S(method), S(file_path)))
        
        return atoms
    
    def extract_performance_patterns(self, content: str, file_path: str) -> List[Atom]:
        """Extract performance optimization patterns."""
        atoms = []
        
        # Caching strategies
        cache_patterns = [
            r'memory.*cache',
            r'redis.*cache',
            r'cache.*invalidation',
            r'cache.*layering'
        ]
        
        for pattern in cache_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                strategy = match.group(0).lower()
                atoms.append(E(S('performance_pattern'), S('caching'), S(strategy)))
                atoms.append(E(S('file'), S(strategy), S(file_path)))
        
        # Database optimization
        db_patterns = [
            r'database.*query.*optimization',
            r'index.*strategy',
            r'query.*planning',
            r'connection.*pooling'
        ]
        
        for pattern in db_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                optimization = match.group(0).lower()
                atoms.append(E(S('performance_pattern'), S('database'), S(optimization)))
                atoms.append(E(S('file'), S(optimization), S(file_path)))
        
        return atoms
    
    def extract_monitoring_concepts(self, content: str, file_path: str) -> List[Atom]:
        """Extract monitoring and observability concepts."""
        atoms = []
        
        # Logging patterns
        logging_patterns = [
            r'structured.*logging',
            r'log.*aggregation',
            r'log.*level.*management',
            r'correlation.*id'
        ]
        
        for pattern in logging_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                concept = match.group(0).lower()
                atoms.append(E(S('monitoring_concept'), S('logging'), S(concept)))
                atoms.append(E(S('file'), S(concept), S(file_path)))
        
        # Metrics and observability
        metrics_patterns = [
            r'performance.*metrics',
            r'business.*metrics',
            r'alerting.*system',
            r'dashboard.*monitoring'
        ]
        
        for pattern in metrics_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                concept = match.group(0).lower()
                atoms.append(E(S('monitoring_concept'), S('metrics'), S(concept)))
                atoms.append(E(S('file'), S(concept), S(file_path)))
        
        return atoms
    
    def extract_error_codes(self, content: str, file_path: str) -> List[Atom]:
        """Extract HTTP error codes and their descriptions."""
        atoms = []
        
        # Pattern for error code tables or lists
        error_patterns = [
            r'(\d{3})\s*[|:]\s*([^|\n]+)',
            r'`(\d{3})`\s*[|:]\s*([^|\n]+)',
            r'(\d{3})\s*-\s*([^.\n]+)',
        ]
        
        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                code = match.group(1).strip()
                description = match.group(2).strip()
                
                # Clean up description
                description = re.sub(r'[|*`]', '', description).strip()
                
                # Try to find associated endpoint
                endpoint = self._find_associated_endpoint(content, match.start())
                
                if endpoint:
                    atoms.append(E(S('error-code'), S(endpoint), S(code), S(description)))
                    self.error_codes[endpoint] = self.error_codes.get(endpoint, {})
                    self.error_codes[endpoint][code] = description
        
        return atoms
    
    def extract_rate_limits(self, content: str, file_path: str) -> List[Atom]:
        """Extract rate limit information."""
        atoms = []
        
        # Pattern for rate limits
        rate_patterns = [
            r'(\d+)\s*requests?\s*per\s*(\w+)',
            r'(\d+)\s*req/\s*(\w+)',
            r'(\d+)\s*/\s*(\w+)',
        ]
        
        for pattern in rate_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                limit = match.group(1).strip()
                period = match.group(2).strip().lower()
                
                # Normalize period
                if period in ['min', 'minute', 'minutes']:
                    period = 'minute'
                elif period in ['hour', 'hours']:
                    period = 'hour'
                elif period in ['day', 'days']:
                    period = 'day'
                
                # Try to find associated endpoint or tier
                endpoint = self._find_associated_endpoint(content, match.start())
                if not endpoint:
                    # Look for tier information
                    tier_match = re.search(r'(free|pro|enterprise)\s+tier', content[:match.start()], re.IGNORECASE)
                    if tier_match:
                        tier = tier_match.group(1).lower()
                        atoms.append(E(S('rate-limit'), S(tier), S(limit), S(period)))
                        self.rate_limits[tier] = {'limit': limit, 'period': period}
                else:
                    atoms.append(E(S('rate-limit'), S(endpoint), S(limit), S(period)))
                    self.rate_limits[endpoint] = {'limit': limit, 'period': period}
        
        return atoms
    
    def extract_tiers(self, content: str, file_path: str) -> List[Atom]:
        """Extract API tier information."""
        atoms = []
        
        # Pattern for tier definitions
        tier_pattern = r'(free|pro|enterprise)\s+tier[^:]*:?\s*([^.\n]*)'
        matches = re.finditer(tier_pattern, content, re.IGNORECASE)
        
        for match in matches:
            tier = match.group(1).lower()
            description = match.group(2).strip()
            
            atoms.append(E(S('tier'), S(tier), S(description)))
            
            # Extract tier-specific rate limits
            rate_limit_match = re.search(r'(\d+)\s*requests?\s*per\s*(\w+)', description, re.IGNORECASE)
            if rate_limit_match:
                limit = rate_limit_match.group(1)
                period = rate_limit_match.group(2).lower()
                atoms.append(E(S('tier-rate-limit'), S(tier), S(limit), S(period)))
        
        return atoms
    
    def extract_authentication(self, content: str, file_path: str) -> List[Atom]:
        """Extract authentication-related facts."""
        atoms = []
        
        # API Key authentication
        if 'api key' in content.lower() or 'bearer' in content.lower():
            atoms.append(E(S('auth-method'), S('api-key')))
            atoms.append(E(S('auth-header'), S('Authorization'), S('Bearer YOUR_API_KEY')))
        
        # Request signing
        if 'sign' in content.lower() and 'request' in content.lower():
            atoms.append(E(S('auth-method'), S('request-signing')))
        
        # IP whitelisting
        if 'whitelist' in content.lower() or 'ip' in content.lower():
            atoms.append(E(S('auth-method'), S('ip-whitelisting')))
        
        return atoms
    
    def _find_associated_endpoint(self, content: str, position: int) -> str:
        """Find the endpoint associated with a parameter or error code."""
        # Look backwards for the most recent endpoint
        before_content = content[:position]
        
        # Find the last endpoint mentioned before this position
        endpoint_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-{}]+)'
        matches = list(re.finditer(endpoint_pattern, before_content, re.IGNORECASE))
        
        if matches:
            last_match = matches[-1]
            endpoint = last_match.group(2).strip()
            # Clean up endpoint
            clean_endpoint = re.sub(r'\{[^}]+\}', '', endpoint)
            if clean_endpoint.endswith('/'):
                clean_endpoint = clean_endpoint[:-1]
            return clean_endpoint
        
        return None
    
    def extract_facts_from_file(self, file_path: str) -> List[Atom]:
        """Extract all facts from a single Markdown file."""
        atoms = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert to HTML for better parsing
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        # Extract different types of facts
        atoms.extend(self.extract_endpoints(content, file_path))
        atoms.extend(self.extract_parameters(content, file_path))
        atoms.extend(self.extract_error_codes(content, file_path))
        atoms.extend(self.extract_rate_limits(content, file_path))
        atoms.extend(self.extract_tiers(content, file_path))
        atoms.extend(self.extract_security_patterns(content, file_path))
        atoms.extend(self.extract_performance_patterns(content, file_path))
        atoms.extend(self.extract_monitoring_concepts(content, file_path))
        atoms.extend(self.extract_authentication(content, file_path))
        
        return atoms
    
    def extract_all_facts(self, docs_dir: str) -> List[Atom]:
        """Extract facts from all Markdown files in the docs directory."""
        all_atoms = []
        
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation directory {docs_dir} not found")
        
        for md_file in docs_path.glob("*.md"):
            print(f"Extracting facts from {md_file.name}...")
            file_atoms = self.extract_facts_from_file(str(md_file))
            all_atoms.extend(file_atoms)
            print(f"  Extracted {len(file_atoms)} facts from {md_file.name}")
        
        return all_atoms

class MeTTaKnowledgeBase:
    """Manages MeTTa knowledge base for API documentation."""
    
    def __init__(self):
        self.metta = MeTTa()
        self.atoms = []
    
    def load_atoms(self, atoms: List[Atom]):
        """Load atoms into the MeTTa environment."""
        self.atoms = atoms
        
        # Add atoms to MeTTa environment
        for atom in atoms:
            try:
                self.metta.run(f"! {atom}")
            except Exception as e:
                print(f"Warning: Could not add atom {atom}: {e}")
    
    def query(self, pattern_atom) -> List[Dict[str, Any]]:
        """Execute a MeTTa pattern query and return results."""
        try:
            space = self.metta.space()
            results = space.query(pattern_atom)
            return results
        except Exception as e:
            print(f"Error executing pattern query: {e}")
            return []
    
    def query_error_codes(self, endpoint: str = None) -> List[Dict[str, Any]]:
        """Query error codes for a specific endpoint or all endpoints."""
        if endpoint:
            query = f"(error-code \"{endpoint}\" $code $desc)"
        else:
            query = "(error-code $endpoint $code $desc)"
        
        results = self.query(query)
        
        error_codes = []
        for result in results:
            if isinstance(result, list) and len(result) >= 3:
                error_codes.append({
                    'endpoint': str(result[0]),
                    'code': str(result[1]),
                    'description': str(result[2])
                })
        
        return error_codes
    
    def query_rate_limits(self, endpoint: str = None) -> List[Dict[str, Any]]:
        """Query rate limits for a specific endpoint or all endpoints."""
        if endpoint:
            query = f"(rate-limit \"{endpoint}\" $limit $period)"
        else:
            query = "(rate-limit $endpoint $limit $period)"
        
        results = self.query(query)
        
        rate_limits = []
        for result in results:
            if isinstance(result, list) and len(result) >= 3:
                rate_limits.append({
                    'endpoint': str(result[0]),
                    'limit': str(result[1]),
                    'period': str(result[2])
                })
        
        return rate_limits
    
    def query_parameters(self, endpoint: str) -> List[Dict[str, Any]]:
        """Query parameters for a specific endpoint."""
        query = f"(param \"{endpoint}\" $param $desc)"
        
        results = self.query(query)
        
        parameters = []
        for result in results:
            if isinstance(result, list) and len(result) >= 3:
                parameters.append({
                    'endpoint': str(result[0]),
                    'parameter': str(result[1]),
                    'description': str(result[2])
                })
        
        return parameters
    
    def query_endpoints(self) -> List[str]:
        """Query all available endpoints."""
        query = "(endpoint $endpoint)"
        
        results = self.query(query)
        
        endpoints = []
        for result in results:
            if isinstance(result, list) and len(result) >= 1:
                endpoints.append(str(result[0]))
        
        return endpoints
    
    def save_atoms(self, filepath: str):
        """Save atoms to a file."""
        with open(filepath, 'w') as f:
            for atom in self.atoms:
                f.write(f"{atom}\n")
        
        print(f"Saved {len(self.atoms)} atoms to {filepath}")
    
    def load_atoms_from_file(self, filepath: str):
        """Load atoms from a file using direct space manipulation."""
        if not os.path.exists(filepath):
            print(f"File {filepath} not found, skipping atom loading")
            return
            
        atoms_added = 0
        space = self.metta.space()
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        # Parse the atom string and add directly to space
                        if line.startswith('(') and line.endswith(')'):
                            # Simple atom parsing - create atoms using E() and S()
                            parts = line[1:-1].split()
                            if len(parts) >= 2:
                                # Create atom like (endpoint /swap) -> E(S('endpoint'), S('/swap'))
                                atom = E(S(parts[0]), S(parts[1]))
                                if len(parts) > 2:
                                    # Handle 3+ part atoms like (error-code 400 "Bad Request")
                                    atom_parts = [S(parts[0])]
                                    for part in parts[1:]:
                                        # Remove quotes if present
                                        clean_part = part.strip('"')
                                        atom_parts.append(S(clean_part))
                                    atom = E(*atom_parts)
                                
                                space.add_atom(atom)
                                atoms_added += 1
                    except Exception as e:
                        print(f"Warning: Could not parse atom '{line}': {e}")
        
        print(f"Loaded {atoms_added} atoms from {filepath}")
    
    def query_security_patterns(self, pattern_type: str = None) -> List[Dict[str, Any]]:
        """Query security patterns like OAuth flows, authentication methods."""
        if pattern_type:
            pattern = E(S('security-flow'), S(pattern_type), V('flow_type'))
        else:
            pattern = E(S('security-flow'), V('pattern'), V('flow_type'))
        
        results = self.query(pattern)
        
        patterns = []
        for result in results:
            if 'flow_type' in result:
                patterns.append({
                    'pattern': str(result.get('pattern', pattern_type)),
                    'flow_type': str(result['flow_type']),
                    'category': 'security'
                })
        
        return patterns
    
    def query_performance_patterns(self, category: str = None) -> List[Dict[str, Any]]:
        """Query performance optimization patterns."""
        if category:
            pattern = E(S('performance-pattern'), S(category), V('pattern'))
        else:
            pattern = E(S('performance-pattern'), V('category'), V('pattern'))
        
        results = self.query(pattern)
        
        patterns = []
        for result in results:
            if 'pattern' in result:
                patterns.append({
                    'category': str(result.get('category', category)),
                    'pattern': str(result['pattern']),
                    'type': 'performance'
                })
        
        return patterns
    
    def query_monitoring_concepts(self, concept_type: str = None) -> List[Dict[str, Any]]:
        """Query monitoring and observability concepts."""
        if concept_type:
            pattern = E(S('monitoring-concept'), S(concept_type), V('concept'))
        else:
            pattern = E(S('monitoring-concept'), V('type'), V('concept'))
        
        results = self.query(pattern)
        
        concepts = []
        for result in results:
            if 'concept' in result:
                concepts.append({
                    'type': str(result.get('type', concept_type)),
                    'concept': str(result['concept']),
                    'category': 'monitoring'
                })
        
        return concepts
    
    def query_advanced_patterns(self, query_text: str) -> List[Dict[str, Any]]:
        """Query for advanced API patterns based on natural language."""
        query_lower = query_text.lower()
        results = []
        
        # Security pattern queries
        if any(word in query_lower for word in ['oauth', 'authentication', 'security', 'auth']):
            results.extend(self.query_security_patterns())
        
        # Performance pattern queries
        if any(word in query_lower for word in ['performance', 'cache', 'optimization', 'speed']):
            results.extend(self.query_performance_patterns())
        
        # Monitoring queries
        if any(word in query_lower for word in ['monitoring', 'logging', 'metrics', 'observability']):
            results.extend(self.query_monitoring_concepts())
        
        # Error handling queries
        if any(word in query_lower for word in ['error', 'exception', 'failure', 'handling']):
            results.extend(self.query_error_codes())
        
        return results

def main():
    """Main ingestion pipeline for MeTTa facts."""
    docs_dir = "../docs"
    atoms_file = "../api_facts.metta"
    
    print("Starting MeTTa fact extraction...")
    
    # Extract facts from documentation
    extractor = MeTTaFactExtractor()
    atoms = extractor.extract_all_facts(docs_dir)
    
    print(f"Total facts extracted: {len(atoms)}")
    
    # Create knowledge base
    kb = MeTTaKnowledgeBase()
    kb.load_atoms(atoms)
    
    # Save atoms to file
    kb.save_atoms(atoms_file)
    
    # Test some queries
    print("\nTesting queries...")
    
    # Query all endpoints
    endpoints = kb.query_endpoints()
    print(f"Found endpoints: {endpoints}")
    
    # Query error codes for /swap endpoint
    if '/swap' in endpoints:
        error_codes = kb.query_error_codes('/swap')
        print(f"Error codes for /swap: {error_codes}")
    
    # Query rate limits
    rate_limits = kb.query_rate_limits()
    print(f"Rate limits: {rate_limits}")
    
    print("\n✅ MeTTa fact extraction completed!")
    print(f"Atoms saved to {atoms_file}")

if __name__ == "__main__":
    main()