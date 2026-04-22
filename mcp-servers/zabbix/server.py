from fastmcp import FastMCP
from pyzabbix import ZabbixAPI
import os

mcp = FastMCP("zabbix")

zapi = ZabbixAPI(os.environ["ZABBIX_URL"])
zapi.login(api_token=os.environ["ZABBIX_TOKEN"])


@mcp.tool()
def get_problems(min_severity: int = 0) -> list:
    """Get active problems. Severity: 0=info, 3=average, 4=high, 5=disaster."""
    return zapi.problem.get(
        severities=list(range(min_severity, 6)),
        selectHosts=["host"],
        output=["objectid", "name", "severity", "clock"],
        limit=20,
    )


@mcp.tool()
def get_hosts() -> list:
    """List all monitored hosts."""
    return zapi.host.get(output=["hostid", "host", "name", "status"])


@mcp.tool()
def get_host_metrics(host: str) -> list:
    """Get latest metric values for a host."""
    hosts = zapi.host.get(filter={"host": host}, output=["hostid"])
    if not hosts:
        return []
    return zapi.item.get(
        hostids=hosts[0]["hostid"],
        output=["name", "lastvalue", "units"],
        sortfield="name",
        limit=20,
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
