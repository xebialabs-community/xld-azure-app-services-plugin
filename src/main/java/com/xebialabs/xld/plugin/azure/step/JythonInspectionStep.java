/**
 * Copyright 2017 XEBIALABS
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
package com.xebialabs.xld.plugin.azure.step;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Writer;
import java.util.Arrays;
import java.util.Map;

import javax.script.ScriptContext;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.SimpleScriptContext;

import com.xebialabs.deployit.plugin.api.flow.ExecutionContext;
import com.xebialabs.deployit.plugin.api.flow.Step;
import com.xebialabs.deployit.plugin.api.flow.StepExitCode;

public class JythonInspectionStep implements Step {

    private String inspectionScript;
    private Map<String, Object> scriptParams;
    private String description;

    public JythonInspectionStep(String inspectionScript, Map<String, Object> scriptParams, String description) {
        this.inspectionScript = inspectionScript.trim();
        this.scriptParams = scriptParams;
        this.description = description;
    }

    @Override
    public int getOrder() {
        return 0;
    }

    @Override
    public String getDescription() {
        return description;
    }

    @Override
    public StepExitCode execute(final ExecutionContext ctx) throws Exception {
        ScriptEngine engine = new ScriptEngineManager().getEngineByName("python");
        if (engine == null) {
            throw new IllegalStateException("Could not find the python/jython, is it on the classpath?");
        }
        InputStream resourceAsStream = Thread.currentThread().getContextClassLoader().getResourceAsStream(inspectionScript);
        if (resourceAsStream == null) {
            throw new IllegalStateException("Inspection script " + inspectionScript + " not found");
        }

        ScriptContext scriptContext = createScriptContext(ctx);

        InputStream sugarPy = Thread.currentThread().getContextClassLoader().getResourceAsStream("syntactical/sugar.py");
        if (sugarPy != null) {
            engine.eval(new InputStreamReader(sugarPy), scriptContext);
        }

        engine.eval(new InputStreamReader(resourceAsStream), scriptContext);
        return StepExitCode.SUCCESS;
    }

    private ScriptContext createScriptContext(ExecutionContext ctx) {
        SimpleScriptContext scriptContext = new SimpleScriptContext();
        scriptContext.setAttribute("inspectionContext", ctx.getInspectionContext(), ScriptContext.ENGINE_SCOPE);
        for (Map.Entry<String, Object> entry : scriptParams.entrySet()) {
            scriptContext.setAttribute(entry.getKey(), entry.getValue(), ScriptContext.ENGINE_SCOPE);
        }
        scriptContext.setWriter(new ConsumerWriter(ctx, false));
        scriptContext.setErrorWriter(new ConsumerWriter(ctx, true));
        return scriptContext;
    }

    private static class ConsumerWriter extends Writer {

        private ExecutionContext ctx;
        private boolean logToError;

        ConsumerWriter(ExecutionContext ctx, boolean logToError) {
            this.ctx = ctx;
            this.logToError = logToError;
        }

        @Override
        public void write(final char[] cbuf, final int off, final int len) throws IOException {
            char[] chars = Arrays.copyOfRange(cbuf, off, off + len);
            if (logToError) {
                ctx.logError(String.valueOf(chars));
            } else {
                ctx.logOutput(String.valueOf(chars));
            }

        }

        @Override
        public void flush() throws IOException {

        }

        @Override
        public void close() throws IOException {

        }
    }
}