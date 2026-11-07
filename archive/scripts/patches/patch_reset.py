with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

content = content.replace(
    """  // Handle mid-stream domain switch
  const handleDomainChange = (newDomain: string) => {
    setSelectedDomain(newDomain);
    checkDomainShift(newDomain);
  };""",
    """  // Handle mid-stream domain switch
  const handleDomainChange = (newDomain: string) => {
    setSelectedDomain(newDomain);
    checkDomainShift(newDomain);
    // Reset stats on domain switch to prevent stale n
    setModelStats({});
    setFlowHistory([]);
  };"""
)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
