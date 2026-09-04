const templates = {
    python: `print("Hello, World from Python!")`,
    cpp: `#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World from C++!" << endl;\n    return 0;\n}`,
    java: `public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World from Java!");\n    }\n}`
};

const languageSelect = document.getElementById('languageSelect');
const codeEditor = document.getElementById('codeEditor');

languageSelect.addEventListener('change', () => {
    codeEditor.value = templates[languageSelect.value];
});

codeEditor.value = templates.python;

async function submitCode() {
    const runBtn = document.getElementById('runBtn');
    const outputBox = document.getElementById('outputBox');
    const statusText = document.getElementById('statusText');
    const timeText = document.getElementById('timeText');

    const language = languageSelect.value;
    const code = codeEditor.value;

    runBtn.disabled = true;
    statusText.innerText = "Executing...";
    outputBox.innerText = "Running on server...";

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language, code })
        });

        const result = await response.json();
        statusText.innerText = result.status;
        timeText.innerText = `${result.executionTime} ms`;
        outputBox.innerText = result.output || "No output returned.";
    } catch (error) {
        statusText.innerText = "ERROR";
        outputBox.innerText = "Failed to run code: " + error.message;
    } finally {
        runBtn.disabled = false;
    }
}