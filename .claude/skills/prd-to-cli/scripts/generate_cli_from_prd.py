#!/usr/bin/env python3
"""
Generate a Python Click CLI project from a PRD.md file about an API.

Parses PRD.md to extract API resources and endpoints, then generates:
- Full project structure with Click CLI
- One subcommand per API resource
- Batch request processor (CSV/TXT support)
- Configuration management (.env)
- Client library boilerplate
"""

import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class PRDParser:
    """Parse PRD.md to extract API resources and endpoints."""

    def __init__(self, prd_content: str):
        self.content = prd_content
        self.resources: Dict[str, Dict] = {}
        self.auth_methods: List[str] = []
        self.api_info = {}

    def parse(self) -> Dict:
        """Parse PRD and extract API structure."""
        self._extract_api_info()
        self._extract_resources()
        self._extract_auth_methods()
        return {
            "api_info": self.api_info,
            "resources": self.resources,
            "auth_methods": self.auth_methods,
        }

    @staticmethod
    def _normalize_resource_token(value: str) -> str:
        """Normalize a resource token for fuzzy matching."""
        return re.sub(r"[^a-z0-9]", "", value.lower())

    def _extract_endpoint_inventory_paths(self) -> List[str]:
        """Extract endpoint paths from markdown bullets like - `/v1/forecast` (with optional trailing text)."""
        return re.findall(r"^\s*-\s*`(/[^`]+)`(?:\s+—.*)?\s*$", self.content, re.MULTILINE)

    def _extract_api_info(self):
        """Extract API title, version, base URL."""
        # Extract title
        title_match = re.search(r"^#\s+(.+?)$", self.content, re.MULTILINE)
        if title_match:
            self.api_info["title"] = title_match.group(1)

        # Extract version
        version_match = re.search(r"\*\*API Version:\*\*\s+(.+?)$", self.content, re.MULTILINE)
        if version_match:
            self.api_info["version"] = version_match.group(1)

        # Extract base URL from multiple PRD styles
        base_url_patterns = [
            r"\*\*Base URL:\*\*\s+`(.+?)`",  # **Base URL:** `https://...`
            r"\*\*Base URL:\*\*\s+(.+?)$",  # **Base URL:** https://...
            r"`base_url`:\s*`(.+?)`",  # - `base_url`: `https://...`
            r"base_url\s*=\s*(https?://\S+)",  # base_url=https://...
        ]
        for pattern in base_url_patterns:
            match = re.search(pattern, self.content, re.MULTILINE)
            if match:
                self.api_info["base_url"] = match.group(1).strip()
                break

        # Extract HTTP library decision selected during doc-to-prd.
        http_library_patterns = [
            r"\*\*HTTP Library:\*\*\s+`?([a-zA-Z0-9_\-]+)`?",
            r"HTTP library:\s*`?([a-zA-Z0-9_\-]+)`?",
            r"`http_library`:\s*`?([a-zA-Z0-9_\-]+)`?",
        ]
        for pattern in http_library_patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                self.api_info["http_library"] = match.group(1).strip().lower()
                break

    def _extract_resources(self):
        """Extract API resources (e.g., pets, users, orders) from section headers."""
        endpoint_paths = self._extract_endpoint_inventory_paths()
        normalized_path_map = {}
        for path in endpoint_paths:
            leaf = path.rstrip("/").split("/")[-1]
            normalized_path_map[self._normalize_resource_token(leaf)] = path

        def resolve_resource_path(resource_name: str) -> str:
            """Resolve a best-fit endpoint path for a resource from endpoint inventory."""
            # 1) Prefer exact first-segment matches from endpoint inventory.
            candidates = []
            for path in endpoint_paths:
                parts = [p for p in path.split("/") if p]
                if not parts:
                    continue
                if self._normalize_resource_token(parts[0]) == self._normalize_resource_token(
                    resource_name
                ):
                    candidates.append(path)

            if candidates:
                # Prefer paths without templated params, then shortest.
                candidates.sort(key=lambda p: ("{" in p, p.count("/"), len(p)))
                return candidates[0]

            # 2) Fallback to leaf-token fuzzy match.
            normalized_item = self._normalize_resource_token(resource_name)
            if normalized_item in normalized_path_map:
                return normalized_path_map[normalized_item]

            # 3) Last resort.
            return f"/{resource_name}"

        # Preferred format in generated PRDs:
        # - Resources: `airquality, archive, forecast`
        resources_line = re.search(
            r"(?:\*\*Resources:\*\*|Resources:)\s*`([^`]+)`",
            self.content,
            re.IGNORECASE,
        )
        if resources_line:
            raw_resources = resources_line.group(1)
            for item in [part.strip().lower() for part in raw_resources.split(",")]:
                if item:
                    resolved_path = resolve_resource_path(item)
                    self.resources[item] = {
                        "name": item,
                        "path": resolved_path,
                        "endpoints": self._extract_endpoints_for_resource(item),
                    }
            if self.resources:
                return

        # Prefer explicit resource headers: "### <Name> Resource"
        explicit_pattern = r"^###\s+([A-Z][A-Za-z]+)\s+Resource$"
        matches = list(re.finditer(explicit_pattern, self.content, re.MULTILINE))

        for match in matches:
            resource_name = match.group(1).lower()
            self.resources[resource_name] = {
                "name": resource_name,
                "path": resolve_resource_path(resource_name),
                "endpoints": self._extract_endpoints_for_resource(resource_name),
            }

    def _extract_endpoints_for_resource(self, resource: str) -> List[Dict]:
        """Extract endpoints for a specific resource."""
        endpoints = []
        # Match #### endpoint patterns (e.g., #### 1. Get User by ID)
        endpoint_pattern = r"^####\s+\d+\.\s+(.+?)$"
        for match in re.finditer(endpoint_pattern, self.content, re.MULTILINE):
            endpoint_desc = match.group(1)
            endpoints.append({"description": endpoint_desc})
        return endpoints

    def _extract_auth_methods(self):
        """Extract authentication methods."""
        if "API Key" in self.content:
            self.auth_methods.append("api_key")
        if "Bearer" in self.content or "OAuth" in self.content:
            self.auth_methods.append("bearer_token")
        if "Basic" in self.content:
            self.auth_methods.append("basic_auth")


class CLIProjectGenerator:
    """Generate full Click CLI project from parsed PRD."""

    def __init__(
        self,
        project_name: str,
        output_dir: str,
        parsed_prd: Dict,
        config: Dict,
    ):
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.parsed_prd = parsed_prd
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.http_library = self._resolve_http_library()
        self.dependencies = self._build_dependencies()

    def _resolve_http_library(self) -> str:
        """Resolve selected HTTP library from PRD metadata/config."""
        requested = (
            self.config.get("http_library")
            or self.parsed_prd.get("api_info", {}).get("http_library")
            or "requests"
        )
        normalized = str(requested).strip().lower()
        if normalized not in {"requests", "httpx", "aiohttp", "urllib3"}:
            return "requests"
        return normalized

    def _build_dependencies(self) -> List[str]:
        """Single source of truth for generated dependencies."""
        deps = [
            "click>=8.0.0",
            "python-dotenv>=0.19.0",
            "pandas>=1.3.0",
            "openpyxl>=3.1.2",
        ]
        if self.http_library == "httpx":
            deps.append("httpx>=0.27.0")
        elif self.http_library == "aiohttp":
            deps.append("aiohttp>=3.9.0")
        elif self.http_library == "urllib3":
            deps.append("urllib3>=2.2.0")
        else:
            deps.append("requests>=2.28.0")
        return deps

    def generate(self):
        """Generate the complete project structure."""
        project_path = self.output_dir / self.project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "output").mkdir(exist_ok=True)

        # Generate files
        self._generate_cli_main(project_path)
        self._generate_client(project_path)
        self._generate_batch_processor(project_path)
        self._generate_env_file(project_path)
        self._generate_init_files(project_path)
        self._generate_requirements(project_path)
        self._generate_pyproject(project_path)
        self._generate_resource_commands(project_path)
        self._generate_shared_templates(project_path)
        self._post_process_python_files(project_path)

        print(f"✅ Project generated: {project_path}")
        return project_path

    def _asset_path(self, filename: str) -> Path:
        """Resolve an asset template path."""
        return Path(__file__).resolve().parent.parent / "assets" / filename

    def _render_asset(self, template_name: str, replacements: Dict[str, str]) -> str:
        """Render an asset template with string replacements."""
        content = self._asset_path(template_name).read_text()
        for key, value in replacements.items():
            content = content.replace(f"{{{key}}}", value)
        return content

    def _generate_cli_main(self, project_path: Path):
        """Generate main CLI entry point."""
        resources = self.parsed_prd["resources"]
        resource_imports = "\n".join(
            f"from src.commands.{name}_commands import {name}_group" for name in resources.keys()
        )

        cli_content = f'''#!/usr/bin/env python3
"""
{self.project_name} - Auto-generated CLI from PRD.md
"""

import click
from src.config import Config

{resource_imports}


@click.group()
@click.option('--config', type=click.Path(exists=False), help='Config file path')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    {self.project_name.replace("_", " ").title()} - API CLI Client

    API: {self.parsed_prd["api_info"].get("title", "Unknown")}
    Version: {self.parsed_prd["api_info"].get("version", "1.0")}
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config_path=config)
    ctx.obj['verbose'] = verbose


# Register resource commands
'''

        for resource_name in resources.keys():
            cli_content += f"cli.add_command({resource_name}_group, '{resource_name}')\n"

        cli_content += '''

@cli.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx', 'sqlite']), default='json')
@click.option('--input-file', type=click.Path(exists=True), help='Batch input file (CSV/TXT)')
@click.option('--output-path', type=click.Path(), default='./output', help='Output directory')
@click.option('--include-timestamp', is_flag=True, help='Include timestamp in output filename')
@click.pass_context
def batch(ctx, format, input_file, output_path, include_timestamp):
    """Process batch requests from input file."""
    from src.batch_processor import BatchProcessor

    processor = BatchProcessor(
        config=ctx.obj['config'],
        output_format=format,
        output_path=output_path,
        include_timestamp=include_timestamp,
        timestamp_format=ctx.obj['config'].get('timestamp_format', '%Y%m%d_%H%M%S'),
    )
    processor.process_file(input_file)


if __name__ == '__main__':
    cli(obj={})
'''

        (project_path / "src" / "cli.py").write_text(cli_content)

    def _generate_client(self, project_path: Path):
        """Generate HTTP client library based on selected HTTP transport."""
        base_url = self.parsed_prd["api_info"].get("base_url", "https://api.example.com")
        title = self.parsed_prd["api_info"].get("title", "API")
        auth_methods = self.parsed_prd["auth_methods"]
        selected = self.http_library

        if selected == "httpx":
            client_content = f'''"""
API Client Library - Auto-generated from PRD.md
"""

from typing import Dict, Any, Optional
import httpx
from src.config import Config


class APIClient:
    """HTTP client for {title} using httpx."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('base_url', '{base_url}')
        self.client = httpx.Client(timeout=30.0)
        self._setup_auth()

    def _setup_auth(self):
        auth_methods = {auth_methods}
        if 'api_key' in auth_methods:
            api_key = self.config.get('api_key', '')
            if api_key:
                self.client.headers.update({{'X-API-Key': api_key}})
        if 'bearer_token' in auth_methods:
            token = self.config.get('api_token', '')
            if token:
                self.client.headers.update({{'Authorization': f'Bearer {{token}}'}})

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{{self.base_url}}{{endpoint}}"
        response = self.client.request(method=method, url=url, params=params, json=data)
        response.raise_for_status()
        if not response.text:
            return {{}}
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        result = self._request('DELETE', endpoint)
        return result if result else {{"status": "deleted"}}
'''
        elif selected == "aiohttp":
            client_content = f'''"""
API Client Library - Auto-generated from PRD.md
"""

import asyncio
from typing import Dict, Any, Optional
import aiohttp
from src.config import Config


class APIClient:
    """HTTP client for {title} using aiohttp."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('base_url', '{base_url}')
        self.headers: Dict[str, str] = {{}}
        self._setup_auth()

    def _setup_auth(self):
        auth_methods = {auth_methods}
        if 'api_key' in auth_methods:
            api_key = self.config.get('api_key', '')
            if api_key:
                self.headers['X-API-Key'] = api_key
        if 'bearer_token' in auth_methods:
            token = self.config.get('api_token', '')
            if token:
                self.headers['Authorization'] = f'Bearer {{token}}'

    async def _request_async(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{{self.base_url}}{{endpoint}}"
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
            async with session.request(method=method, url=url, params=params, json=data) as response:
                response.raise_for_status()
                text = await response.text()
                if not text:
                    return {{}}
                return await response.json()

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        return asyncio.run(self._request_async(method, endpoint, params=params, data=data))

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        result = self._request('DELETE', endpoint)
        return result if result else {{"status": "deleted"}}
'''
        elif selected == "urllib3":
            client_content = f'''"""
API Client Library - Auto-generated from PRD.md
"""

import json
from typing import Dict, Any, Optional
import urllib3
from urllib.parse import urlencode
from src.config import Config


class APIClient:
    """HTTP client for {title} using urllib3."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('base_url', '{base_url}')
        self.headers: Dict[str, str] = {{}}
        self.http = urllib3.PoolManager()
        self._setup_auth()

    def _setup_auth(self):
        auth_methods = {auth_methods}
        if 'api_key' in auth_methods:
            api_key = self.config.get('api_key', '')
            if api_key:
                self.headers['X-API-Key'] = api_key
        if 'bearer_token' in auth_methods:
            token = self.config.get('api_token', '')
            if token:
                self.headers['Authorization'] = f'Bearer {{token}}'

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        query = urlencode(params or {{}}) if params else ''
        url = f"{{self.base_url}}{{endpoint}}"
        if query:
            url = f"{{url}}?{{query}}"
        body = json.dumps(data).encode('utf-8') if data is not None else None
        headers = dict(self.headers)
        if body is not None:
            headers['Content-Type'] = 'application/json'
        response = self.http.request(method, url, body=body, headers=headers, timeout=30.0)
        if response.status >= 400:
            raise RuntimeError(f"HTTP {{response.status}}: {{response.data.decode('utf-8', errors='ignore')}}")
        payload = response.data.decode('utf-8', errors='ignore').strip()
        if not payload:
            return {{}}
        return json.loads(payload)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        result = self._request('DELETE', endpoint)
        return result if result else {{"status": "deleted"}}
'''
        else:
            client_content = f'''"""
API Client Library - Auto-generated from PRD.md
"""

from typing import Dict, Any, Optional
import requests
from src.config import Config


class APIClient:
    """HTTP client for {title} using requests."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('base_url', '{base_url}')
        self.session = requests.Session()
        self._setup_auth()

    def _setup_auth(self):
        auth_methods = {auth_methods}
        if 'api_key' in auth_methods:
            api_key = self.config.get('api_key', '')
            if api_key:
                self.session.headers.update({{'X-API-Key': api_key}})
        if 'bearer_token' in auth_methods:
            token = self.config.get('api_token', '')
            if token:
                self.session.headers.update({{'Authorization': f'Bearer {{token}}'}})

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{{self.base_url}}{{endpoint}}"
        response = self.session.request(method=method, url=url, params=params, json=data, timeout=30)
        response.raise_for_status()
        if not response.text:
            return {{}}
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        result = self._request('DELETE', endpoint)
        return result if result else {{"status": "deleted"}}
'''

        (project_path / "src" / "client.py").write_text(client_content)

    def _generate_batch_processor(self, project_path: Path):
        """Generate batch request processor."""
        processor_content = '''"""
Batch request processor for CSV/TXT input files.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from src.client import APIClient
from src.config import Config
from src.output import save_output


class BatchProcessor:
    """Process batch requests from CSV or TXT files."""

    def __init__(
        self,
        config: Config,
        output_format: str = 'json',
        output_path: str = './output',
        include_timestamp: bool = False,
        timestamp_format: str = '%Y%m%d_%H%M%S',
    ):
        self.config = config
        self.client = APIClient(config)
        self.output_format = output_format
        self.output_path = Path(output_path)
        self.include_timestamp = include_timestamp
        self.timestamp_format = timestamp_format
        self.output_path.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process input file (CSV or TXT)."""
        file_path = Path(file_path)

        if file_path.suffix.lower() == '.csv':
            requests_list = self._parse_csv(file_path)
        elif file_path.suffix.lower() == '.txt':
            requests_list = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        results = []
        for request_data in requests_list:
            try:
                result = self._execute_request(request_data)
                results.append(result)
                print(f"✅ Processed: {request_data.get('endpoint', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({"error": str(e)})

        self._save_results(results)
        return results

    def _parse_csv(self, file_path: Path) -> List[Dict]:
        """Parse CSV file."""
        requests_list = []
        with open(file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                requests_list.append(dict(row))
        return requests_list

    def _parse_txt(self, file_path: Path) -> List[Dict]:
        """Parse TXT file (JSON lines format)."""
        requests_list = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    requests_list.append(json.loads(line))
        return requests_list

    def _execute_request(self, request_data: Dict) -> Dict:
        """Execute a single request."""
        method = request_data.get('method', 'GET').upper()
        endpoint = request_data.get('endpoint', '/')

        if method == 'GET':
            return self.client.get(endpoint)
        elif method == 'POST':
            return self.client.post(endpoint, request_data.get('data', {}))
        elif method == 'PUT':
            return self.client.put(endpoint, request_data.get('data', {}))
        elif method == 'DELETE':
            return self.client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def _save_results(self, results: List[Dict]):
        """Save results in specified format."""
        output_file = save_output(
            payload=results,
            output_format=self.output_format,
            output_dir=str(self.output_path),
            stem="results",
            include_timestamp=self.include_timestamp,
            timestamp_format=self.timestamp_format,
        )
        print(f"Results saved to: {output_file}")
'''

        (project_path / "src" / "batch_processor.py").write_text(processor_content)

    def _generate_env_file(self, project_path: Path):
        """Generate .env.example file."""
        env_content = f"""# API Configuration
base_url={self.parsed_prd["api_info"].get("base_url", "https://api.example.com")}
api_key=your_api_key_here
api_token=your_bearer_token_here

# Output Configuration
timestamp_format=%Y%m%d_%H%M%S
output_format=json
# Supported values: json, csv, xlsx, sqlite
include_timestamp=false

# Batch Processing
batch_input_format=csv
batch_output_path=./output

# Logging
log_level=INFO
verbose=false
"""

        (project_path / ".env.example").write_text(env_content)

    def _generate_init_files(self, project_path: Path):
        """Generate __init__.py files."""
        (project_path / "src" / "commands").mkdir(exist_ok=True)
        (project_path / "src" / "__init__.py").write_text("")
        (project_path / "src" / "commands" / "__init__.py").write_text("")

    def _generate_requirements(self, project_path: Path):
        """Generate requirements.txt."""
        requirements = "\n".join(self.dependencies) + "\n"
        (project_path / "requirements.txt").write_text(requirements)

    def _generate_pyproject(self, project_path: Path):
        """Generate pyproject.toml from asset template."""
        template_path = self._asset_path("pyproject_template.toml")
        template = template_path.read_text()

        description = self.parsed_prd["api_info"].get(
            "title",
            f"{self.project_name.replace('_', ' ').title()} API CLI",
        )
        safe_project_name = self.project_name.replace("_", "-")

        dependencies = [f'"{dep}"' for dep in self.dependencies]
        dependencies_block = ",\n    ".join(dependencies)
        dev_dependencies = [
            '"pytest>=8.0.0"',
            '"ruff>=0.6.0"',
            '"black>=24.0.0"',
            '"isort>=5.13.0"',
        ]
        dev_dependencies_block = ",\n    ".join(dev_dependencies)

        pyproject = (
            template.replace("{PROJECT_NAME}", safe_project_name)
            .replace("{DESCRIPTION}", description)
            .replace("{DEPENDENCIES}", dependencies_block)
            .replace("{DEV_DEPENDENCIES}", dev_dependencies_block)
            .replace("{CONSOLE_SCRIPT}", safe_project_name)
        )

        (project_path / "pyproject.toml").write_text(pyproject)

    def _generate_shared_templates(self, project_path: Path):
        """Generate reusable template-based project files."""
        safe_project_name = self.project_name.replace("_", "-")
        resource_names = list(self.parsed_prd["resources"].keys())
        resource_targets = []
        resource_help_lines = []
        for resource in resource_names[:8]:
            target = f"{resource}-list"
            resource_help_lines.append(
                f'\t@echo "  make {target:<12} Example: uv run $(PROJECT_NAME) {resource} list"'
            )
            resource_targets.extend(
                [
                    f"{target}:",
                    f"\tuv run $(PROJECT_NAME) {resource} list",
                    "",
                ]
            )

        replacements = {
            "PROJECT_NAME": self.project_name,
            "PROJECT_NAME_DASH": safe_project_name,
            "API_TITLE": self.parsed_prd["api_info"].get("title", "API"),
            "BASE_URL": self.parsed_prd["api_info"].get("base_url", "https://api.example.com"),
            "HTTP_LIBRARY": self.http_library,
            "TIMESTAMP_FORMAT": "%Y%m%d_%H%M%S",
            "ENV_PREFIX": re.sub(r"[^A-Z0-9]", "_", self.project_name.upper()),
            "RESOURCE_HELP_LINES": "\n".join(resource_help_lines)
            if resource_help_lines
            else '\t@echo "  (no resource groups discovered from PRD)"',
            "RESOURCE_TARGETS": "\n".join(resource_targets).rstrip(),
        }

        files_to_render = [
            ("config_template.py", project_path / "src" / "config.py"),
            ("utils_template.py", project_path / "src" / "utils.py"),
            ("logger_template.py", project_path / "src" / "logger.py"),
            ("output_template.py", project_path / "src" / "output.py"),
            ("test_cli_template.py", project_path / "tests" / "test_cli.py"),
            ("makefile_template.mk", project_path / "Makefile"),
        ]

        (project_path / "tests").mkdir(exist_ok=True)
        (project_path / "tests" / "__init__.py").write_text("")

        for template_name, dest in files_to_render:
            rendered = self._render_asset(template_name, replacements)
            dest.write_text(rendered)

    def _generate_resource_commands(self, project_path: Path):
        """Generate Click command files for each resource."""
        (project_path / "src" / "commands").mkdir(exist_ok=True)

        for resource_name, resource_data in self.parsed_prd["resources"].items():
            self._generate_resource_command_file(project_path, resource_name, resource_data)

    def _generate_resource_command_file(
        self, project_path: Path, resource_name: str, resource_data: Dict
    ):
        """Generate a command file for a specific resource."""
        resource_path = resource_data.get("path", f"/{resource_name}")

        command_content = f'''"""
CLI commands for {resource_name} resource.
"""

import click
from src.client import APIClient


@click.group()
@click.pass_context
def {resource_name}_group(ctx):
    """Manage {resource_name.capitalize()} resources."""
    ctx.obj = ctx.obj or {{}}


@{resource_name}_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.pass_context
def list(ctx, format):
    """List all {resource_name}."""
    client = APIClient(ctx.obj['config'])
    try:
        results = client.get('{resource_path}')
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"Format {{format}} not yet implemented")
    except Exception as e:
        click.echo(f"Error: {{e}}", err=True)


@{resource_name}_group.command()
@click.argument('id')
@click.pass_context
def get(ctx, id):
    """Get a {resource_name[:-1]} by ID."""
    client = APIClient(ctx.obj['config'])
    try:
        result = client.get('{resource_path}/{{id}}')
        import json
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {{e}}", err=True)


@{resource_name}_group.command()
@click.option('--data', type=str, help='JSON data for the {resource_name[:-1]}')
@click.pass_context
def create(ctx, data):
    """Create a new {resource_name[:-1]}."""
    client = APIClient(ctx.obj['config'])
    try:
        import json
        payload = json.loads(data) if data else {{}}
        result = client.post('{resource_path}', payload)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {{e}}", err=True)
'''

        file_path = project_path / "src" / "commands" / f"{resource_name}_commands.py"
        file_path.write_text(command_content)

    def _post_process_python_files(self, project_path: Path):
        """Best-effort lint/format/import-fix pass for generated Python files."""
        targets = ["src", "tests"]

        def run_step(label: str, cmd: List[str]):
            try:
                result = subprocess.run(
                    cmd,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print(f"✅ Post-process: {label}")
                else:
                    print(
                        f"⚠️ Post-process skipped/failed ({label}): {result.stderr.strip() or result.stdout.strip()}"
                    )
            except Exception as exc:
                print(f"⚠️ Post-process skipped ({label}): {exc}")

        # Prefer ruff when available (includes lint fixes + formatting + import sorting).
        if shutil.which("ruff"):
            run_step("ruff check --fix", ["ruff", "check", *targets, "--fix"])
            run_step("ruff format", ["ruff", "format", *targets])
            return

        # Fallback chain when ruff is not available.
        if shutil.which("isort"):
            run_step("isort", ["isort", *targets])
        if shutil.which("black"):
            run_step("black", ["black", *targets])

        # Minimal syntax lint fallback.
        py_files = []
        for rel in ("src", "tests"):
            base = project_path / rel
            if base.exists():
                py_files.extend(str(p.relative_to(project_path)) for p in base.rglob("*.py"))
        if py_files:
            run_step("py_compile", ["python", "-m", "py_compile", *py_files])


def load_prd(prd_path: str) -> str:
    """Load PRD.md file content."""
    with open(prd_path) as f:
        return f.read()


def main(prd_path: str, output_dir: str, config: Dict) -> Path:
    """Main generation workflow."""
    # Load and parse PRD
    prd_content = load_prd(prd_path)
    parser = PRDParser(prd_content)
    parsed_prd = parser.parse()

    # Generate project
    project_name = config.get("project_name", "api_client")
    generator = CLIProjectGenerator(
        project_name=project_name,
        output_dir=output_dir,
        parsed_prd=parsed_prd,
        config=config,
    )
    project_path = generator.generate()
    return project_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_cli_from_prd.py <prd_file> <output_dir> [project_name]")
        sys.exit(1)

    prd_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    project_name = sys.argv[3] if len(sys.argv) > 3 else "api_client"

    config = {"project_name": project_name}
    project = main(prd_file, output_dir, config)
    print(f"\n✅ Project created at: {project}")
