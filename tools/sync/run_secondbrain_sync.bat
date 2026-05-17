@echo off
cd /d "G:\O meu disco\Claude-NTICS-Projetos"
python tools\sync\secondbrain_sync.py --quiet >> "G:\O meu disco\Claude-NTICS-Projetos\.tmp\logs\secondbrain_sync.log" 2>&1
