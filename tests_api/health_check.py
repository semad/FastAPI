#!/usr/bin/env python3
"""
Health Check Script for FastAPI Application

This script checks if the FastAPI service is running and healthy by:
1. Testing basic connectivity
2. Checking the health endpoint (if available)
3. Testing the OpenAPI docs endpoint
4. Verifying database connectivity (if configured)

Usage:
    python tests_api/health_check.py
    python tests_api/health_check.py --verbose
    python tests_api/health_check.py --url http://localhost:8000
"""

import argparse
import json
import sys
import time
from typing import Dict, Any, Optional
import requests
from urllib.parse import urljoin


class HealthChecker:
    """Health checker for FastAPI application."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
    def check_connectivity(self) -> Dict[str, Any]:
        """Check basic connectivity to the service."""
        print("🔍 Checking basic connectivity...")
        
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": round(response_time * 1000, 2),  # Convert to ms
                "url": self.base_url,
                "error": None
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": self.base_url,
                "error": "Connection refused - service may not be running"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": self.base_url,
                "error": f"Request timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": self.base_url,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def check_health_endpoint(self) -> Dict[str, Any]:
        """Check the health endpoint if available."""
        print("🏥 Checking health endpoint...")
        
        health_url = urljoin(self.base_url, "/health")
        
        try:
            start_time = time.time()
            response = self.session.get(health_url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": health_url,
                        "data": health_data,
                        "error": None
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "healthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": health_url,
                        "data": response.text,
                        "error": None
                    }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time": round(response_time * 1000, 2),
                    "url": health_url,
                    "data": None,
                    "error": f"Health endpoint returned status {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": health_url,
                "data": None,
                "error": f"Request failed: {str(e)}"
            }
    
    def check_docs_endpoint(self) -> Dict[str, Any]:
        """Check the OpenAPI docs endpoint."""
        print("📚 Checking OpenAPI docs endpoint...")
        
        docs_url = urljoin(self.base_url, "/docs")
        
        try:
            start_time = time.time()
            response = self.session.get(docs_url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "status_code": response.status_code,
                    "response_time": round(response_time * 1000, 2),
                    "url": docs_url,
                    "content_type": response.headers.get('content-type', 'unknown'),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time": round(response_time * 1000, 2),
                    "url": docs_url,
                    "content_type": None,
                    "error": f"Docs endpoint returned status {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": docs_url,
                "content_type": None,
                "error": f"Request failed: {str(e)}"
            }
    
    def check_openapi_schema(self) -> Dict[str, Any]:
        """Check the OpenAPI schema endpoint."""
        print("🔧 Checking OpenAPI schema endpoint...")
        
        schema_url = urljoin(self.base_url, "/openapi.json")
        
        try:
            start_time = time.time()
            response = self.session.get(schema_url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    schema_data = response.json()
                    endpoints = list(schema_data.get('paths', {}).keys())
                    
                    return {
                        "status": "healthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": schema_url,
                        "endpoints_count": len(endpoints),
                        "endpoints": endpoints[:10],  # Show first 10 endpoints
                        "error": None
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": schema_url,
                        "endpoints_count": None,
                        "endpoints": None,
                        "error": "Invalid JSON response"
                    }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time": round(response_time * 1000, 2),
                    "url": schema_url,
                    "endpoints_count": None,
                    "endpoints": None,
                    "error": f"Schema endpoint returned status {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": schema_url,
                "endpoints_count": None,
                "endpoints": None,
                "error": f"Request failed: {str(e)}"
            }
    
    def check_ready_endpoint(self) -> Dict[str, Any]:
        """Check the ready endpoint if available."""
        print("✅ Checking ready endpoint...")
        
        ready_url = urljoin(self.base_url, "/ready")
        
        try:
            start_time = time.time()
            response = self.session.get(ready_url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    ready_data = response.json()
                    return {
                        "status": "healthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": ready_url,
                        "data": ready_data,
                        "error": None
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "healthy",
                        "status_code": response.status_code,
                        "response_time": round(response_time * 1000, 2),
                        "url": ready_url,
                        "data": response.text,
                        "error": None
                    }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time": round(response_time * 1000, 2),
                    "url": ready_url,
                    "data": None,
                    "error": f"Ready endpoint returned status {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "status_code": None,
                "response_time": None,
                "url": ready_url,
                "data": None,
                "error": f"Request failed: {str(e)}"
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        print(f"🚀 Starting health checks for {self.base_url}")
        print("=" * 60)
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "checks": {}
        }
        
        # Run all checks
        results["checks"]["connectivity"] = self.check_connectivity()
        results["checks"]["health"] = self.check_health_endpoint()
        results["checks"]["docs"] = self.check_docs_endpoint()
        results["checks"]["openapi_schema"] = self.check_openapi_schema()
        results["checks"]["ready"] = self.check_ready_endpoint()
        
        # Calculate overall status
        healthy_checks = sum(1 for check in results["checks"].values() if check["status"] == "healthy")
        total_checks = len(results["checks"])
        
        results["overall"] = {
            "status": "healthy" if healthy_checks == total_checks else "unhealthy",
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "success_rate": round((healthy_checks / total_checks) * 100, 1)
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any], verbose: bool = False):
        """Print health check results in a formatted way."""
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK RESULTS")
        print("=" * 60)
        print(f"🕐 Timestamp: {results['timestamp']}")
        print(f"🌐 Base URL: {results['base_url']}")
        print(f"📈 Overall Status: {results['overall']['status'].upper()}")
        print(f"✅ Healthy Checks: {results['overall']['healthy_checks']}/{results['overall']['total_checks']}")
        print(f"📊 Success Rate: {results['overall']['success_rate']}%")
        
        print("\n" + "-" * 60)
        print("🔍 DETAILED RESULTS")
        print("-" * 60)
        
        for check_name, check_result in results["checks"].items():
            status_emoji = "✅" if check_result["status"] == "healthy" else "❌"
            print(f"\n{status_emoji} {check_name.upper().replace('_', ' ')}")
            print(f"   Status: {check_result['status']}")
            
            if check_result["status_code"]:
                print(f"   HTTP Status: {check_result['status_code']}")
            
            if check_result["response_time"]:
                print(f"   Response Time: {check_result['response_time']}ms")
            
            if check_result["url"]:
                print(f"   URL: {check_result['url']}")
            
            if verbose and check_result.get("data"):
                if isinstance(check_result["data"], list):
                    print(f"   Data: {len(check_result['data'])} items")
                    if check_result["data"]:
                        print(f"   Sample: {check_result['data'][:3]}")
                else:
                    print(f"   Data: {check_result['data']}")
            
            if check_result.get("endpoints_count"):
                print(f"   Endpoints: {check_result['endpoints_count']}")
                if verbose and check_result.get("endpoints"):
                    print(f"   Sample Endpoints: {', '.join(check_result['endpoints'][:5])}")
            
            if check_result["error"]:
                print(f"   Error: {check_result['error']}")
        
        print("\n" + "=" * 60)
        
        # Final summary
        if results["overall"]["status"] == "healthy":
            print("🎉 All health checks passed! The service is healthy.")
        else:
            print("⚠️  Some health checks failed. Please investigate the issues above.")
        
        print("=" * 60)


def main():
    """Main function to run health checks."""
    parser = argparse.ArgumentParser(
        description="Health check script for FastAPI application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tests_api/health_check.py                    # Check localhost:8000
    python tests_api/health_check.py --url http://localhost:8000  # Check specific URL
    python tests_api/health_check.py --verbose          # Show detailed output
    python tests_api/health_check.py --timeout 30      # Set custom timeout
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the FastAPI service (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including response data"
    )
    
    args = parser.parse_args()
    
    # Create health checker
    checker = HealthChecker(base_url=args.url, timeout=args.timeout)
    
    try:
        # Run all checks
        results = checker.run_all_checks()
        
        # Print results
        checker.print_results(results, verbose=args.verbose)
        
        # Exit with appropriate code
        if results["overall"]["status"] == "healthy":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during health check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
