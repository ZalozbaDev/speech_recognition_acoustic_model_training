''' Created on Mon Jun 5 11:40:19 2023

    UASR and BAS configuration files templates.

    @author: ivan

Copyright (c) 2023 Fraunhofer IKTS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DEFAULT_ITP = '''
## UASR extension script
## - HSB database

## Function overwrites                                                          # -------------------------------------
".-LAB_export" "function" ?instance if
  /disarm -LAB_export_esps /disarm -LAB_export =;
end

## Function overwrites                                                          # -------------------------------------
".-LAB_import" "function" ?instance if
  /disarm -LAB_import_esps /disarm -LAB_import =;
end

'''

PROJECT_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<ProjectConfiguration version="4.0.0">
  <name>$PROJECT$</name>
  <RecordingConfiguration>
    <url>RECS/</url>
    <captureScope>SESSION</captureScope>
  </RecordingConfiguration>
  <PromptConfiguration>
    <promptsUrl>$PROJECT$_script.xml</promptsUrl>
    <InstructionsFont>
      <family>SansSerif</family>
    </InstructionsFont>
    <PromptFont>
      <family>SansSerif</family>
    </PromptFont>
    <DescriptionFont>
      <family>SansSerif</family>
    </DescriptionFont>
    <automaticPromptPlay>false</automaticPromptPlay>
    <PromptBeep>
      <beepGainRatio>1.0</beepGainRatio>
    </PromptBeep>
  </PromptConfiguration>
  <Speakers>
    <speakersUrl>$PROJECT$_speakers.xml</speakersUrl>
  </Speakers>
</ProjectConfiguration>'''

SCRIPT_FRONT = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE script SYSTEM "SpeechRecPrompts_4.dtd">
<script id="$PROJECT$">
  <metadata>
    <key/>
    <value/>
  </metadata>
  <recordingscript>
    <section speakerdisplay="true">'''

SCRIPT_BACK = '''
 	 </section>
  </recordingscript>
</script>'''

CLASS_HEADER = '''
## UASR class definition file
## - VerbMobil Database
##
##   first  column: model name
##   second column: number of states
##   third  column: voice/unvoiced information
##   fourth column: abstract model for SMG reclassification

 .	3	0.0	[nsp]
 #	3	0.0	[nsp]
'''
UASR_HEADER = '''
## UASR configuration file
## - Verbmobil database

'''
