import {createServer} from "node:http";
import {readFileSync,statSync,createReadStream,readdirSync,renameSync,writeFileSync} from "node:fs";
import {resolve,extname,basename} from "node:path";
import {createHash} from "node:crypto";
import {chromium} from "playwright";

const root=resolve(new URL(".",import.meta.url).pathname);
const evidenceRoot=resolve(process.argv[2]||"artifacts/android-p1");
const port=4173;
const mime={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"text/javascript; charset=utf-8"};
const server=createServer((req,res)=>{
  const raw=(req.url||"/").split("?")[0];
  const path=resolve(root,raw==="/"?"index.html":raw.slice(1));
  if(!path.startsWith(root)){res.writeHead(403);res.end();return}
  try{const st=statSync(path);if(!st.isFile())throw new Error();res.writeHead(200,{"content-type":mime[extname(path)]||"application/octet-stream"});createReadStream(path).pipe(res)}
  catch{res.writeHead(404);res.end("not found")}
});
await new Promise(ok=>server.listen(port,"127.0.0.1",ok));

const browser=await chromium.launch({headless:true});
const context=await browser.newContext({
  viewport:{width:412,height:915},
  isMobile:true,
  hasTouch:true,
  deviceScaleFactor:1,
  userAgent:"Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36",
  recordVideo:{dir:evidenceRoot,size:{width:412,height:915}},
  reducedMotion:"no-preference"
});
const page=await context.newPage();
const steps=[];
async function step(name,action,delay=1250){await action();steps.push({name,at_ms:Date.now()-started});await page.waitForTimeout(delay)}
const started=Date.now();
await step("Open prototype home",()=>page.goto(`http://127.0.0.1:${port}/`));
await step("Notification deep-link -> Decision Inbox",()=>page.getByTestId("notification").getByRole("button",{name:"فتح"}).tap());
await step("Inspect Evidence bottom sheet",()=>page.getByRole("button",{name:"فحص الأدلة"}).tap());
await step("Close Evidence sheet",()=>page.getByRole("button",{name:"إغلاق"}).tap());
await step("Request Changes owner intent",()=>page.getByRole("button",{name:"طلب تعديلات"}).tap());
await step("Open Project from bottom navigation",()=>page.getByRole("button",{name:"المشاريع"}).tap());
await step("Open artifact Evidence",()=>page.locator('[data-screen="project"] [data-action="open-evidence"]').tap());
await step("Close artifact Evidence",()=>page.getByRole("button",{name:"إغلاق"}).tap());
await step("Exercise bounded Pause intent",()=>page.getByRole("button",{name:"إيقاف مؤقت"}).tap());
await step("Open Pulse",()=>page.getByRole("button",{name:"النبض"}).tap());
await step("Open Pulse project",()=>page.locator('[data-screen="pulse"] [data-action="open-project"]').tap());
await step("Open More/System",()=>page.getByRole("button",{name:"المزيد"}).tap());
await step("Enable Reduced Motion",()=>page.getByRole("button",{name:"تقليل الحركة"}).tap());
await page.waitForTimeout(1600);
const finalState=await page.evaluate(()=>window.__ucState);
await page.screenshot({path:resolve(evidenceRoot,"android-final.png"),fullPage:true});
const video=page.video();
await page.close();
const tempVideo=await video.path();
await context.close();
await browser.close();
server.close();

const targetVideo=resolve(evidenceRoot,"android-p1-interaction.webm");
renameSync(tempVideo,targetVideo);
const bytes=readFileSync(targetVideo);
const sha256=createHash("sha256").update(bytes).digest("hex");
const pngBytes=readFileSync(resolve(evidenceRoot,"android-final.png"));
const pngSha=createHash("sha256").update(pngBytes).digest("hex");
const manifest={
  schema_version:"1.0",
  evidence_type:"ANDROID_SEMANTIC_COMPANION_P1_PROTOTYPE",
  platform_target:"Android",
  implementation_surface:"mobile web semantic prototype under Android touch emulation",
  prototype_fixture:true,
  runtime_authority:false,
  stage8_opened:false,
  live_host_dispatch:false,
  viewport:{width:412,height:915,touch:true},
  video:{file:basename(targetVideo),sha256,bytes:bytes.length,duration_ms:Date.now()-started},
  final_screenshot:{file:"android-final.png",sha256:pngSha,bytes:pngBytes.length},
  steps,
  final_state:finalState
};
writeFileSync(resolve(evidenceRoot,"android-evidence-manifest.json"),JSON.stringify(manifest,null,2));
console.log(JSON.stringify(manifest,null,2));
