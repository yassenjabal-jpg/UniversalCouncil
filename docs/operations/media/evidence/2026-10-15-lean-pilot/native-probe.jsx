// Read-only native probe: never closes or modifies a project.
try {
    var file = new File('E:/GPT/2026-10-14/referenced-chatgpt-conversation-this-is-an/work/native-probe.json');
    file.encoding = 'UTF-8';
    if (!file.open('w')) throw new Error('Cannot write native probe receipt');
    file.write('{"tool":"Adobe After Effects 2026","status":"PASS","current_session":true,"version":"' + app.version + '","scope":"native_script_execution_only_no_delivery_claim","project_modified":false}');
    file.close();
} catch (error) {
    var failure = new File('E:/GPT/2026-10-14/referenced-chatgpt-conversation-this-is-an/work/native-probe-error.txt');
    failure.open('w'); failure.write(String(error)); failure.close();
}
