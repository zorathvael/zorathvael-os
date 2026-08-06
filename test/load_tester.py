import concurrent.futures
import time
from lib.core_modules.workflow_engine.workflow_orchestrator import WorkflowOrchestrator

def simulate_user(user_id: int) -> dict:
    orchestrator = WorkflowOrchestrator()
    start = time.time()
    res = orchestrator.execute_scenario(user_id, f"Stress test request from user {user_id}", "openai")
    duration = (time.time() - start) * 1000
    return {"user_id": user_id, "status": res["status"], "latency_ms": duration}

def run_load_test(concurrency: int) -> dict:
    print(f"Running load test with concurrency = {concurrency} users...")
    start_total = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(simulate_user, i) for i in range(concurrency)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    total_time = time.time() - start_total
    success_count = sum(1 for r in results if r["status"] == "success")
    avg_latency = sum(r["latency_ms"] for r in results) / concurrency
    
    return {
        "concurrency": concurrency,
        "total_requests": concurrency,
        "success_count": success_count,
        "error_count": concurrency - success_count,
        "total_time_sec": total_time,
        "avg_latency_ms": avg_latency,
        "throughput_req_sec": concurrency / total_time
    }

if __name__ == "__main__":
    for c in [10, 50, 100, 500, 1000]:
        metrics = run_load_test(c)
        print(metrics)
