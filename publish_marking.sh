for repo in */; do
    cd $repo
    gh repo set-default `git remote get-url origin`
    gh issue create --title "Feedback" -F marking.md
    cd ..
done
