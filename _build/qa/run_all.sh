#!/bin/bash
# v14 の QA を順番に実行（出力は ../qa_v14_*.txt、撮影は ../ref_shots/v14_*）。python3 -m http.server 8766 を scratchpad 直下で起動しておくこと
cd "$(dirname "$0")/.." || exit 1
python3 build.py > /dev/null
python3 validate.py > ../qa_v14_validate.txt 2>&1
node qa/check.mjs > ../qa_v14_check.txt 2>&1
node qa/form.mjs > ../qa_v14_form.txt 2>&1
node qa/herofv.mjs > ../qa_v14_herofv.txt 2>&1
node qa/faq.mjs > ../qa_v14_faq.txt 2>&1
node qa/fit.mjs > ../qa_v14_fit.txt 2>&1
node qa/anchors.mjs > ../qa_v14_anchors.txt 2>&1
node qa/edge.mjs > ../qa_v14_edge.txt 2>&1
node qa/jsfail.mjs > ../qa_v14_jsfail.txt 2>&1
node qa/nomask.mjs > ../qa_v14_nomask.txt 2>&1
node qa/motion.mjs > ../qa_v14_motion.txt 2>&1
node qa/hdr.mjs 1023 1024 1100 1199 1200 1279 1280 1440 > ../qa_v14_hdr.txt 2>&1
node qa/hero1024.mjs > ../qa_v14_hero.txt 2>&1
node qa/images.mjs > ../qa_v14_images.txt 2>&1
node qa/h1lines.mjs > ../qa_v14_h1lines.txt 2>&1
node qa/shots_v14.mjs > ../qa_v14_shots.txt 2>&1
echo finished > ../qa_v14_done.txt
