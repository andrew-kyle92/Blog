// ********** Logic for the Joke API page **********

// ########## fetch calls ##########
const fetchJokes = async (url) => {
    const jokeUrl = new URL(url);
    let jokeData = await fetch(jokeUrl)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return jokeData;
}

// ** Display category options if custom is selected in the drop-down box **
var dropDwnBox = document.getElementById("categoryOptions");
var checkBoxOptions = document.getElementById("cat-options");
dropDwnBox.addEventListener("change", () => {
    if(dropDwnBox.value == "Custom"){
        checkBoxOptions.style.display = "flex";
    }
    else{
        checkBoxOptions.style.display = "none";
    }
});

function revealDelivery(id){
    let delivery = document.getElementById(id);
    let revealed = delivery.classList.contains("revealed");
    if(!revealed){
        delivery.style.color = "#7e7c7c";
        delivery.style.textShadow = "1px 1px 5px";
        delivery.classList.add("revealed");
    }
    else{
        delivery.classList.remove("revealed");
        delivery.style.color = "transparent";
        delivery.style.textShadow = "1px 1px 8px #fff";
    }
    
}

const getJokes = async () => {
    var categoryOptions = document.getElementById("categoryOptions");
    var customOptions = document.querySelectorAll("#cat-options input");
    var flagsSet = document.querySelectorAll("#joke-flags input");
    var jokeType = document.getElementById("jokeType");
    var keywords = document.getElementById("keywords");
    var baseUrl = "https://v2.jokeapi.dev/joke/";
    var completeUrl = `${baseUrl}`
    // getting the category
    if(categoryOptions.value == "Any"){
        completeUrl += "Any";
    }
    else{
        // if custom is selected, then finding all the options
        let seperator = ",";
        cats = []
        for(let i = 0; i < customOptions.length; i++){
            if(customOptions[i].checked){
                cats.push(customOptions[i].value);
            }
        }
        if(cats != 0){
            for(let i = 0; i < cats.length; i++){
                if(i == cats.length - 1){
                    completeUrl += cats[i];
                }
                else{
                    completeUrl += cats[i] + seperator;
                }
            }
        }
        else{
            completeUrl += "Any";
        }
        
    }
    // finding all flags
    flags = []
    for(let i = 0; i < flagsSet.length; i++){
        if(flagsSet[i].checked){
            flags.push(flagsSet[i].value);
        }
    }
    if(flags.length > 0){
        completeUrl += "?blacklistFlags=";
        let seperator = ","
        for(let i = 0; i < flags.length; i++){
            if(i == flags.length - 1){
                completeUrl += flags[i];
            }
            else{
                completeUrl += flags[i] + seperator;
            }
        }
    }
    // joke type (single, twopart)
    if(jokeType.value != ''){
        // adding ? if none is already present
        completeUrl += completeUrl.includes("?") ? `&type=${jokeType.value}` : `?type=${jokeType.value}`;
    }
    // adding keywords
    if(keywords.value != ''){
        completeUrl += completeUrl.includes("?") ? `&contains=${keywords.value}` : `?contains${keywords.value}`;
    }
    completeUrl = completeUrl.includes("?") ? `${completeUrl}&amount=5` : `${completeUrl}?amount=5`;
    // pulling Joke data;
    let jokeData = await fetchJokes(completeUrl);
    if(!jokeData["error"]){
        // Clearing previous joke data
        // getting the results div
        var parentDiv = document.getElementById("jokeResultsDiv");
        var children = parentDiv.childElementCount;
        if(children > 0){
            while(children > 0){
                parentDiv.removeChild(parentDiv.lastElementChild);
                children -= 1;
            }
        }
        // creating the joke content
        var containsMultiJokes = Object.keys(jokeData).includes("jokes");
        if(containsMultiJokes){
            var jokes = jokeData["jokes"];
            for(let i = 0; i < jokes.length; i++){
                //creating the outer div
                var outerDiv = document.createElement("div");
                outerDiv.setAttribute("id", jokes[i]["id"]);
                outerDiv.setAttribute("class", "jokeDiv");
                parentDiv.appendChild(outerDiv);
                // creating id and category text
                var jokeContentDiv = document.getElementById(jokes[i]["id"]);
                var jokeDesc = document.createElement("div");
                jokeDesc.setAttribute("id", "jokeDesc");
                jokeContentDiv.appendChild(jokeDesc);
                var idText = document.createElement("span");
                idText.setAttribute("class", "joke-id-text");
                idText.innerText = `Joke ID: ${jokes[i]["id"]}`;
                jokeDesc.appendChild(idText);
                var catText = document.createElement("span");
                catText.setAttribute("class", "joke-category");
                catText.innerHTML = `Category: ${jokes[i]["category"]}`
                jokeDesc.appendChild(catText);
                // determing the format of the joke based on the type
                if(jokes[i]["type"] == "single"){
                    // if type=single, creating just one div
                    var jokeTextDiv = document.createElement("div");
                    jokeTextDiv.setAttribute("class", `jokeTextDiv ${jokes[i]["id"]}`);
                    jokeContentDiv.appendChild(jokeTextDiv);
                    //creating the paragraph within the div
                    var jokeTextParent = document.getElementsByClassName(`${jokes[i]["id"]}`)[0];
                    var jokeText = document.createElement("span");
                    jokeText.setAttribute("class", "joke-text");
                    jokeText.innerHTML = jokes[i]["joke"];
                    jokeTextParent.appendChild(jokeText);
                }
                else{
                    // if type=twopart, creating two divs
                    var jokeTextDiv = document.createElement("div");
                    jokeTextDiv.setAttribute("class", `jokeTextDiv ${jokes[i]["id"]}`);
                    jokeContentDiv.appendChild(jokeTextDiv);
                    //creating the setup and delivery paragraphs within the div
                    var jokeTextParent = document.getElementsByClassName(`${jokes[i]["id"]}`)[0];
                    var jokeSetup = document.createElement("span");
                    jokeSetup.setAttribute("class", "joke-text");
                    jokeSetup.innerHTML = jokes[i]["setup"];
                    jokeTextParent.appendChild(jokeSetup);
                    var deliveryDiv = document.createElement("div");
                    deliveryDiv.setAttribute("id", `joke-delivery-div`);
                    jokeTextParent.appendChild(deliveryDiv);
                    var jokeDelivery = document.createElement("span");
                    jokeDelivery.setAttribute("id", `joke-${jokes[i]["id"]}`);
                    jokeDelivery.setAttribute("class", "joke-delivery");
                    jokeDelivery.innerHTML = jokes[i]["delivery"];
                    deliveryDiv.appendChild(jokeDelivery);
                    var revealCheckBox = document.createElement("input");
                    revealCheckBox.setAttribute("type", "checkbox");
                    revealCheckBox.setAttribute("onclick", `revealDelivery('joke-${jokes[i]["id"]}')`);
                    revealCheckBox.setAttribute("title", "Reveal Delivery");
                    deliveryDiv.appendChild(revealCheckBox);
                }
                var hr = document.createElement("hr");
                parentDiv.appendChild(hr);
            }
        }
        else{
            //creating the outer div
            var outerDiv = document.createElement("div");
            outerDiv.setAttribute("id", jokeData["id"]);
            outerDiv.setAttribute("class", "jokeDiv");
            parentDiv.appendChild(outerDiv);
            // creating id text
            var jokeContentDiv = document.getElementById(jokeData["id"]);
            var jokeDesc = document.createElement("div");
            jokeDesc.setAttribute("id", "jokeDesc");
            jokeContentDiv.appendChild(jokeDesc);
            var idText = document.createElement("span");
            idText.setAttribute("class", "joke-id-text");
            idText.innerText = `Joke ID: ${jokeData["id"]}`;
            jokeDesc.appendChild(idText);
            var catText = document.createElement("span");
            catText.setAttribute("class", "joke-category");
            catText.innerHTML = `Category: ${jokeData["category"]}`
            jokeDesc.appendChild(catText);
            // determing the format of the joke based on the type
            if(jokeData["type"] == "single"){
                // if type=single, creating just one div
                var jokeTextDiv = document.createElement("div");
                jokeTextDiv.setAttribute("class", `jokeTextDiv ${jokeData["id"]}`);
                jokeContentDiv.appendChild(jokeTextDiv);
                //creating the paragraph within the div
                var jokeTextParent = document.getElementsByClassName(`${jokeData["id"]}`)[0];
                var jokeText = document.createElement("span");
                jokeText.setAttribute("class", "joke-text");
                jokeText.innerHTML = jokeData["joke"];
                jokeTextParent.appendChild(jokeText);
            }
            else{
                // if type=twopart, creating two divs
                var jokeTextDiv = document.createElement("div");
                jokeTextDiv.setAttribute("class", `jokeTextDiv ${jokeData["id"]}`);
                jokeContentDiv.appendChild(jokeTextDiv);
                //creating the setup and delivery paragraphs within the div
                var jokeTextParent = document.getElementsByClassName(`${jokeData["id"]}`)[0];
                var jokeSetup = document.createElement("span");
                jokeSetup.setAttribute("class", "joke-text");
                jokeSetup.innerHTML = jokeData["setup"];
                jokeTextParent.appendChild(jokeSetup);
                var deliveryDiv = document.createElement("div");
                deliveryDiv.setAttribute("id", `joke-delivery-div`);
                jokeTextParent.appendChild(deliveryDiv);
                var jokeDelivery = document.createElement("span");
                jokeDelivery.setAttribute("id", `joke-${jokeData["id"]}`);
                jokeDelivery.setAttribute("class", "joke-delivery");
                jokeDelivery.innerHTML = jokeData["delivery"];
                deliveryDiv.appendChild(jokeDelivery);
                var revealCheckBox = document.createElement("input");
                revealCheckBox.setAttribute("type", "checkbox");
                revealCheckBox.setAttribute("onclick", `revealDelivery('joke-${jokeData["id"]}')`);
                revealCheckBox.setAttribute("title", "Reveal Delivery");
                deliveryDiv.appendChild(revealCheckBox);
            }
        }
        
    }
    else{
        console.log(jokes["message"]);
        console.log(jokes["causedBy"]);
    }
}