// webworker.js

// Setup your project to serve `py-worker.js`. You should also serve
// `pyodide.js`, and all its associated `.asm.js`, `.json`,
// and `.wasm` files as well:
importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js");

async function loadPyodideAndPackages() {
    //self.pyodide = await loadPyodide();
    //await self.pyodide.loadPackage(["numpy", "pytz"]);
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage("micropip");
    const micropip = self.pyodide.pyimport("micropip");
    await micropip.install('urllib3==1.26.18');
    await micropip.install('elasticsearch==8.4.3');
    await micropip.install('geopy==2.3.0');
    await micropip.install('lxml==4.9.3');
    await micropip.install('pycountry==23.12.11');
    await micropip.install('python-dotenv==1.0.0');
    await micropip.install('requests==2.28.2');
    await micropip.install('pyodide-http');
    await micropip.install("ssl"); // required by elasticsearch, could be removed?
    await micropip.install('https://www.piwheels.org/simple/docopt/docopt-0.6.2-py2.py3-none-any.whl');
    await micropip.install('stlscraper-1.0-py3-none-any.whl');
    self.pyodide.runPython(`import pyodide_http; pyodide_http.patch_all(); import requests; import os;`);
    self.pyodide.runPython(`os.environ["AIRBNB_API_KEY"] = "d306zoyjsyarp7ifhu67rjxn52tv0t20"`);
    self.pyodide.runPython(`os.environ["CORS_API_KEY"] = "EZWTLwVEqFnaycMzdhBx"`);
    self.pyodide.runPython(`import stl.main;`);
}

self.onmessage = async (event) => {
    // make sure loading is done
    //await pyodideReadyPromise;
    // Don't bother yet with this line, suppose our API is built in such a way:
    const { id, python, ...context } = event.data;
    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
        self[key] = context[key];
    }
    // Now is the easy part, the one that is similar to working in the main thread:
    if (id == 1) {
        let results = await loadPyodideAndPackages();
        self.postMessage({ results, id });
    } else {
        try {
            self.pyodide.FS.writeFile("/data.json", self['data'], { encoding: "utf8" });
            let results = await self.pyodide.runPythonAsync(python);
            let file = self.pyodide.FS.readFile("/data.json", { encoding: "utf8" });
            self.postMessage({ results: file, id });
        } catch (error) {
            self.postMessage({ error: error.message, id });
        }
    }
};