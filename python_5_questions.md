# 🚀 Python for DevOps: Complete 5-Day Automation Roadmap

Sabhi problems, challenges aur solutions ka poora nichod yahan ek hi block mein hai:

---

### 📂 1. Log Analysis & Azure Blobs
* **Problem:** Azure Blob Storage se server logs download karke CPU data nikalna.
* **Challenges:** Regex fail ho raha tha kyunki log format badal gaya tha (`%` vs `°C`).
* **Solution:** Flexible Regex `r"CPU.*:\s*(\d+)"` use kiya taaki koi bhi metric name ho, value pakdi jaye.
* **Key Code:** `re.search(r"CPU.*:\s*(\d+)", line)`

### ⚡ 2. Async vs Threading (API Concurrency)
* **Problem:** 3+ microservices ki health ek saath check karni thi (Parallelism).
* **Challenges:** `ModuleNotFoundError` server par, jise `pip install aiohttp` se solve kiya.
* **Solution:** `asyncio.gather(*tasks)` use karke execution time ko 15 sec se ghatakar 5 sec kiya.
* **Key Code:** `async with aiohttp.ClientSession() as session: ...`

### 💾 3. Disk Monitoring & Automated Alerts
* **Problem:** Server storage 60% cross hone par turant email alert chahiye tha.
* **Challenges:** Security ki wajah se normal Gmail password block ho raha tha.
* **Solution:** `shutil.disk_usage` for monitoring + Google "App Password" for `smtplib` authentication.
* **Key Code:** `if usage_percent > 60: send_alert_email()`

### ☸️ 4. Kubernetes (Kind Cluster) Monitoring
* **Problem:** Docker-based K8s (Kind) mein failed pods ko automate karke dhoondna.
* **Challenges:** Grafana vs Python ka logic: Grafana sirf dikhata hai (Passive), Python script action leti hai (Active).
* **Solution:** `kubernetes` client library use karke pod status aur event reasons extract kiye.
* **Key Code:** `config.load_kube_config()` aur `v1.list_pod_for_all_namespaces()`

### 💸 5. Azure Cost Management & FinOps
* **Problem:** Monthly billing report generate karna aur "Modern Usage" errors handle karna.
* **Challenges:** 1. Auth Error: Solution - Azure VM par Managed Identity "On" ki.
    2. Attribute Error: `ModernUsageDetail` mein `kind_properties_value` nahi tha.
* **Solution:** `getattr()` function use kiya taaki Legacy aur Modern dono APIs support ho sakein.
* **Final Code:**
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient

def fetch_azure_costs(sub_id):
    client = ConsumptionManagementClient(DefaultAzureCredential(), f"/subscriptions/{sub_id}")
    costs = {}
    for item in client.usage_details.list(scope=f"/subscriptions/{sub_id}"):
        name = getattr(item, 'meter_category', 'Other')
        val = getattr(item, 'cost_in_pricing_currency', getattr(item, 'pretax_cost', 0))
        costs[name] = costs.get(name, 0) + float(val or 0)
    for k, v in sorted(costs.items(), key=lambda x: x[1], reverse=True):
        print(f"{k:<30} | ${v:.2f}")

fetch_azure_costs("80570f80-b315-47a7-9a48-1df4e6fbee0d")
