// One bounded native AE backup of the same system pilot; no GUI automation.
(function () {
    var root = 'E:/GPT/2026-10-14/referenced-chatgpt-conversation-this-is-an';
    var work = root + '/work';
    function receipt(name, value) {
        var f = new File(work + '/' + name); f.encoding='UTF-8';
        if (!f.open('w')) throw new Error('Cannot write receipt: ' + name);
        f.write(value); f.close();
    }
    try {
        // -m starts a separate instance; do not replace any existing user project.
        if (app.project && app.project.numItems > 0) throw new Error('Refusing to replace nonempty project');
        app.beginUndoGroup('Lean system pilot native backup');
        if (!app.project) app.newProject();
        var W=1920,H=1080,D=41.766667,FPS=30;
        var cobalt=[0.055,0.30,0.82], ivory=[0.96,0.945,0.90], charcoal=[0.08,0.09,0.10], plum=[0.40,0.08,0.22];
        var comp=app.project.items.addComp('LEAN_DAY24_SYSTEM_PILOT_NATIVE',W,H,1,D,FPS);
        comp.comment='TECHNICAL PILOT ONLY — temporary test voice, NOT accepted Owner narration. Same pilot rerouted once from Descript. Ambiment — Kevin MacLeod (incompetech.com), CC BY 3.0. Audio source is the temporary Descript review mix; individual stems unavailable in current plan.';
        function solid(name,color,a,b) {var l=comp.layers.addSolid(color,name,W,H,1,D);l.inPoint=a;l.outPoint=b;return l;}
        function fade(l,a,b) {l.property('Opacity').setValueAtTime(a,0);l.property('Opacity').setValueAtTime(a+0.35,100);l.property('Opacity').setValueAtTime(b-0.25,100);l.property('Opacity').setValueAtTime(b,0);}
        function text(name,content,x,y,size,color,a,b) {
            var l=comp.layers.addText(content),td=l.property('Source Text').value;
            td.font='SegoeUI';td.fontSize=size;td.fillColor=color;td.applyFill=true;td.applyStroke=false;
            td.justification=ParagraphJustification.CENTER_JUSTIFY;
            try { td.composerEngine=ComposerEngine.UNIVERSAL_TYPE_ENGINE; } catch (e) {}
            try { td.direction=ParagraphDirection.RIGHT_TO_LEFT; } catch (e2) {}
            l.property('Source Text').setValue(td);l.inPoint=a;l.outPoint=b;
            var box=l.sourceRectAtTime(a,false);l.property('Anchor Point').setValue([box.left+box.width/2,box.top+box.height/2]);
            l.property('Position').setValue([x,y]);fade(l,a,b);return l;
        }
        function rect(name,x,y,w,h,color,a,b) {
            var l=comp.layers.addShape();l.name=name;l.inPoint=a;l.outPoint=b;
            var g=l.property('Contents').addProperty('ADBE Vector Group');
            var r=g.property('Contents').addProperty('ADBE Vector Shape - Rect');r.property('Size').setValue([w,h]);
            var f=g.property('Contents').addProperty('ADBE Vector Graphic - Fill');f.property('Color').setValue(color);
            l.property('Position').setValue([x,y]);return l;
        }
        solid('COBALT_QUESTION',cobalt,0,5);
        text('AR_QUESTION','من قرر أن اليوم 24 ساعة؟',960,245,78,ivory,0,5);
        text('HERO_24','24',960,610,230,ivory,0.4,5);
        for(var i=0;i<24;i++) {
            var angle=i*2*Math.PI/24,x=960+250*Math.sin(angle),y=590-250*Math.cos(angle);
            var tick=rect('DIVISION_'+i,x,y,8,50,i<12?ivory:plum,0,5);
            tick.property('Rotation').setValue(i*15);tick.property('Opacity').setValueAtTime(0.5+i*0.06,0);tick.property('Opacity').setValueAtTime(0.7+i*0.06,100);
        }
        solid('IVORY_EXPLANATION',ivory,5,17);
        text('DAY_NIGHT','12 ساعة نهار + 12 ساعة ليل',960,285,72,charcoal,5,10);
        for(var j=0;j<24;j++) {var seg=rect('12_PLUS_12_'+j,240+j*62,610,52,150,j<12?cobalt:charcoal,5,10);fade(seg,5+j*0.018,10);}
        text('NIGHT_SYSTEM','الليل… ومراقبة النجوم',960,290,72,charcoal,10,17);
        for(var k=0;k<12;k++) {var star=rect('DECAN_MARKER_'+k,350+(k%6)*240,520+Math.floor(k/6)*160,24,24,k%3==0?plum:cobalt,10,17);star.property('Rotation').setValue(45);fade(star,10+k*0.06,17);}
        solid('EVIDENCE_COBALT',cobalt,17,25);
        var evidence=app.project.importFile(new ImportOptions(new File(work+'/UniversalCouncil/docs/operations/media/pilots/assets/met_549494_11.150.50b1.jpg')));
        var mount=rect('EVIDENCE_MOUNT',960,540,1100,820,ivory,17,25);fade(mount,17,25);
        var image=comp.layers.add(evidence);image.inPoint=17;image.outPoint=25;
        var factor=Math.min(1000/evidence.width,670/evidence.height)*100;image.property('Scale').setValue([factor,factor]);image.property('Position').setValue([960,515]);fade(image,17,25);
        text('AUTHENTIC_SOURCE','The Met — 11.150.50b1 — Public Domain',960,915,28,ivory,17,25);
        solid('IVORY_UNEQUAL',ivory,25,31);
        text('UNEQUAL_HOURS','ساعات غير متساوية',960,285,84,charcoal,25,31);
        for(var n=0;n<12;n++) {var bar=rect('UNEQUAL_'+n,340+n*112,625,65,160,cobalt,25,31);bar.property('Scale').setValueAtTime(25,[100,45+(n%4)*32]);bar.property('Scale').setValueAtTime(30.5,[100,100]);fade(bar,25,31);}
        solid('IVORY_EQUAL',ivory,31,36);
        text('EQUAL_HOURS','لاحقًا: ساعات متساوية',960,285,80,charcoal,31,36);
        for(var q=0;q<24;q++) {var equal=rect('EQUAL_'+q,240+q*62,625,48,160,q%6==0?plum:cobalt,31,36);fade(equal,31+q*0.012,36);}
        solid('COBALT_END',cobalt,36,D);
        text('CLOSING','نظام تشكّل خطوةً بعد خطوة',960,450,76,ivory,36,D);
        text('ENDING_24','24',960,720,130,ivory,36.2,D);
        var audio=app.project.importFile(new ImportOptions(new File(work+'/pilot-temp-mix.wav')));
        var mix=comp.layers.add(audio);mix.name='TEMP_TEST_MIX_NOT_OWNER_VOICE';mix.audioEnabled=true;
        mix.property('Audio').property('Audio Levels').setValue([-1.6,-1.6]);
        // Output adjustment is native AE; ffmpeg is used only for input demux/QC or technical encoding.
        var rq=app.project.renderQueue.items.add(comp),om=rq.outputModule(1),templates=om.templates,chosen='Lossless';
        for(var t=0;t<templates.length;t++) if(/H.264/i.test(templates[t])) {chosen=templates[t];break;}
        om.applyTemplate(chosen);
        var extension=chosen=='Lossless'?'.avi':'.mp4';
        om.file=new File(work+'/LEAN_DAY24_NATIVE_RENDER'+extension);
        app.project.save(new File(root+'/outputs/LEAN_DAY24_SYSTEM_PILOT_NATIVE.aep'));
        app.endUndoGroup();
        receipt('native-build.json','{"status":"PASS_BUILT_NOT_QC_APPROVED","tool":"Adobe After Effects 2026","composition":"LEAN_DAY24_SYSTEM_PILOT_NATIVE","width":1920,"height":1080,"fps":30,"duration_seconds":'+D+',"output_template":"'+chosen+'","render_path":"'+om.file.fsName.replace(/\\/g,'/')+'","audio_gain_db":-1.6,"gui_actions":0}');
    } catch(error) {receipt('native-build-error.txt',String(error)+' line '+error.line);}
})();
