// Targeted QC repairs to our generated project only, in a separate native instance.
(function(){
var root='E:/GPT/2026-10-14/referenced-chatgpt-conversation-this-is-an';
function note(name,message){var f=new File(root+'/work/'+name);f.encoding='UTF-8';f.open('w');f.write(message);f.close();}
try {
 if(app.project && app.project.numItems>0) throw new Error('Refusing to replace nonempty project');
 app.open(new File(root+'/outputs/LEAN_DAY24_SYSTEM_PILOT_NATIVE.aep'));
 var comp=app.project.renderQueue.item(1).comp;
 comp.layer('TEMP_TEST_MIX_NOT_OWNER_VOICE').property('Audio').property('Audio Levels').setValue([-2.1,-2.1]);
 function textProperty(prefix){for(var i=1;i<=comp.numLayers;i++){var group=comp.layer(i).property('ADBE Text Properties');if(group){var prop=group.property('ADBE Text Document');if(prop.value.text.indexOf(prefix)===0)return prop;}}throw new Error('Missing generated text: '+prefix);}
 var title=textProperty('12 ساعة نهار'), td=title.value;
 td.text='اثنتا عشرة ساعة للنهار ومثلها لليل';td.fontSize=68;title.setValue(td);
 var source=textProperty('The Met'), st=source.value;
 st.fillColor=[0.08,0.09,0.10];try{st.direction=ParagraphDirection.LEFT_TO_RIGHT;}catch(e){};source.setValue(st);
 app.project.renderQueue.item(1).outputModule(1).file=new File(root+'/work/LEAN_DAY24_NATIVE_QC_RENDER.mp4');
 app.project.save(new File(root+'/outputs/LEAN_DAY24_SYSTEM_PILOT_NATIVE_QC.aep'));
 note('native-qc-repair.json','{"status":"PASS_TARGETED_REPAIR_BUILT_NOT_FINAL_APPROVAL","gain_db":-2.1,"rtl_numeric_header":"replaced with Arabic words","evidence_credit":"charcoal on ivory LTR","gui_actions":0}');
}catch(error){note('native-qc-repair-error.txt',String(error)+' line '+error.line);}
})();
