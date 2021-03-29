# On windows, run this in git bash or WSL

if ! command -v dot &> /dev/null
then
    echo "dot could not be found. Please install graphviz"
    exit
fi

echo "Profiling started at " $(date -d "today" +"%m%d%H%M")

time python -m cProfile -o profiles/profile.pstats nith_result.py --roll-pattern=17...

python gprof2dot.py -f pstats profiles/profile.pstats | dot -Tpng -o profiles/$(date -d "today" +"%Y%m%d_%H%M%S").png

echo 'Done'