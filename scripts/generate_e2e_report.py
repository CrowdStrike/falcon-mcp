"""
Generate a static HTML report from test result data
"""

import json
import re
import sys
from html import escape
from typing import Any


def generate_static_report(
    data: list[dict[str, Any]],
    template_path: str = "scripts/test_results_viewer.html",
    output_path: str = "static_test_report.html",
) -> None:
    """
    Generates a static HTML report from test result data.

    Args:
        data (list): A list of test result dictionaries.
        template_path (str): The path to the HTML template file to extract styles from.
        output_path (str): The path to write the final static HTML file.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()
        match = re.search(r"<style>(.*?)</style>", html_template, re.DOTALL)
        style_content = match.group(1) if match else ""
    except FileNotFoundError:
        print(
            f"Warning: Could not read styles from {template_path}. Using default styles."
        )
        style_content = "body { font-family: sans-serif; } /* Basic fallback styles */"

    # --- Group and process data ---
    total_runs = len(data)
    successful_runs = sum(1 for run in data if run.get("status") == "success")
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

    # Group first by module, then by test name
    grouped_by_module: dict[str, dict[str, Any]] = {}
    for run in data:
        module_name = run.get("module_name", "Unknown Module")
        test_name = run.get("test_name", "Unnamed Test")

        if module_name not in grouped_by_module:
            grouped_by_module[module_name] = {}

        if test_name not in grouped_by_module[module_name]:
            grouped_by_module[module_name][test_name] = []

        grouped_by_module[module_name][test_name].append(run)

    # Further group by model within each test
    for module_name, tests in grouped_by_module.items():
        for test_name, runs in tests.items():
            grouped_by_model: dict[str, list[dict[str, Any]]] = {}
            for run in runs:
                model_name = run.get("model_name", "Unnamed Model")
                grouped_by_model.setdefault(model_name, []).append(run)
            grouped_by_module[module_name][test_name] = grouped_by_model

    # --- Build HTML body content ---
    body_content = f"""
    <h1>MCP E2E Static Test Report</h1>
    <div id="summary">
        <h2>Summary</h2>
        <p>Total Tests Run: <span>{total_runs}</span></p>
        <p>Success Rate: <span>{success_rate:.2f}%</span></p>
    </div>
    <div id="results-container">
    """

    for module_name, tests in sorted(grouped_by_module.items()):
        body_content += f'<div class="module-group"><h2>{escape(module_name)}</h2>'
        for test_name, models in sorted(tests.items()):
            body_content += f'<div class="test-group"><h3>{escape(test_name)}</h3>'
            for model_name, runs in sorted(models.items()):
                body_content += (
                    f'<div class="model-group"><h4>{escape(model_name)}</h4>'
                )
                body_content += '<div class="run-grid">'
                for run in sorted(runs, key=lambda x: x.get("run_number", 0)):
                    status_class = escape(run.get("status", "unknown"))
                    run_html = f"""
                    <div class="test-run {status_class}">
                        <h5>Run {run.get("run_number", "#")} - {status_class.upper()}</h5>
                    """
                    if status_class == "failure" and run.get("failure_reason"):
                        reason = escape(run["failure_reason"])
                        run_html += f'<p><strong>Failure Reason:</strong></p><pre class="failure-reason"><code>{reason}</code></pre>'

                    agent_result = escape(
                        run.get("agent_result", "No result") or "No result"
                    )
                    run_html += f"""
                        <details>
                            <summary>Agent Result</summary>
                            <div class="agent-result"><pre><code>{agent_result}</code></pre></div>
                        </details>
                    """

                    if run.get("tools_used"):
                        tools_json = escape(json.dumps(run["tools_used"], indent=2))
                        run_html += f"""
                            <details>
                                <summary>Tools Used ({len(run["tools_used"])})</summary>
                                <div class="tools-content"><pre><code>{tools_json}</code></pre></div>
                            </details>
                        """
                    else:
                        run_html += "<p>No tools were used.</p>"

                    run_html += "</div>"
                    body_content += run_html
                body_content += "</div></div>"
            body_content += "</div>"
        body_content += "</div>"
    body_content += "</div>"

    # --- Assemble the final HTML ---
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Test Results</title>
    <style>{style_content}</style>
</head>
<body>
    {body_content}
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Successfully generated static report: {output_path}")


if __name__ == "__main__":
    test_results_path = sys.argv[1] if len(sys.argv) > 1 else "test_results.json"
    try:
        with open(test_results_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
        generate_static_report(test_data)
    except FileNotFoundError:
        print("Error: test_results.json not found. Please run the tests first.")
    except json.JSONDecodeError:
        print(
            "Error: Could not parse test_results.json. The file might be corrupted or empty."
        )
