const runCode = async () => {
  try {
    const res = await axios.post("http://127.0.0.1:5000/run", {
      code: translated
    });

    const result = res.data.result;

    setRunOutput(
      "Output:\n" +
      result.stdout +
      "\nErrors:\n" +
      result.stderr
    );

  } catch (err) {
    setRunOutput("Execution failed");
  }
};