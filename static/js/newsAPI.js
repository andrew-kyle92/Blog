// ########## fetch calls ##########
const getArticles = async () => {
    var qValue = document.getElementsByClassName("kwInput")[0].value;
    var sortValue = document.getElementsByClassName("sortInput")[0].value;
    var amtValue = Number(document.getElementsByClassName("amtInput")[0].value);
    const articleUrl = 'search-articles?' + new URLSearchParams({
        "q": qValue,
        "sort_by": sortValue,
        "amount": amtValue
    })
    let articleData = await fetch(articleUrl)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return articleData;
}

function createPosts(articles){
    var newsArticleDiv = document.getElementById("unoriginalNews");

    for(let i = 0; i < articles.length; i++){
        let date = new Date(articles[i]["publishedAt"]);
        let newDiv = document.createElement("div");
        newDiv.setAttribute("class", "post-preview newsApi");
        newsArticleDiv.appendChild(newDiv);
        // getting the newly created div
        let postDiv = document.getElementsByClassName("newsApi")[0];
        let divDesc = document.createElement("p");
        divDesc.setAttribute("class", "articleSource");
        divDesc.innerHTML = "Brought to you by: <a href='https://newsapi.org/' target='blank'>NewsAPI</a>"
        let newA = document.createElement("a");
        let author = articles[i]["author"] != null ? articles[i]["author"].replace(" ", "") : "Unknown"
        newA.setAttribute("href", `/post?post_id=${author}&publishDate=${articles[i]["publishedAt"]}&API=True`);
        newA.innerHTML = `<h2 class="post-title">${articles[i]["title"]}</h2><h3 class="post-subtitle">${articles[i]["description"].substring(0, 100) + "..."}</h3>`;
        let newP = document.createElement("p");
        newP.setAttribute("class", "post-meta");
        newP.innerHTML = `Posted By <a href="#${author}">${author}</a> on ${date.toLocaleString()}`;
        let newHr = document.createElement("hr")
        postDiv.append(divDesc);
        postDiv.appendChild(newA);
        postDiv.appendChild(newP);
        postDiv.appendChild(newHr);
    }
}

const searchArticles = async () => {
    var keyword = document.getElementsByClassName("kwInput")[0];
    if(keyword.value != ''){
        var articles = await getArticles();
        var newsArticleDiv = document.getElementById("unoriginalNews");
        var articleList = articles["articles"];
        while(newsArticleDiv.childElementCount > 0){
            newsArticleDiv.removeChild(newsArticleDiv.lastElementChild);
        }
        if(newsArticleDiv.childElementCount == 0){
            if(articleList.length > 0){
                // creating article content for each article
                createPosts(articleList);
            }
        }
    }
    else{
        alert("You must enter a keyword");
    }

}