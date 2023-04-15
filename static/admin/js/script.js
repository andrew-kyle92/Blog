window.addEventListener("load", () => {
    // ########## Fetch calls ##########
    const fetchTable = async (table) => {
        const tableURL = "/fetch-table-data?" + new URLSearchParams({
           "table":  table
        });
        let tableFetch = await fetch(tableURL)
            .then(async (response) => {
                const data = await response.json();
                return data
            });
        return tableFetch
    }
    // ########## Creation Functions
    function createTable(data){
        let dbTableName = Object.keys(data)[0];
        let dbCols = data[dbTableName]["columns"];
        let dbData = data[dbTableName]["data"];
        // parent div
        let parentDiv = document.getElementById("body-middle");
        // table creation
        let table = document.createElement("table");
        parentDiv.appendChild(table);
        table.setAttribute("id", `${dbTableName}`);
        table.setAttribute("data-collapsed", "false");
        // thead creation & content
        let thead = document.createElement("thead");
        table.appendChild(thead);
        let head_tr = document.createElement("tr");
        thead.appendChild(head_tr);
        for(let i = 0; i < dbCols.length; i++){
            let th = document.createElement("th");
            th.innerText = dbCols[i];
            head_tr.appendChild(th);
        }
        // tbody creation and content
        let tbody = document.createElement("tbody");
        table.appendChild(tbody);
        for(let i = 0; i < dbData.length; i++){
            let body_tr = document.createElement("tr");
            for(let j = 0; j < dbCols.length; j++){
                let body_td = document.createElement("td");
                let text = String(dbData[i][dbCols[j]]);
                body_td.innerText = text.length > 15 ? text.substring(0, 15) + "..." : text;
                body_td.title = text;
                // body_td.innerText = text;
                body_tr.appendChild(body_td);
            }
            tbody.appendChild(body_tr);
        }

    }

    // ########## OnEvent Functions ##########
    // Adding onclick events to all table divs
    let allTables = document.getElementsByClassName("table-item");
    for(let i = 0; i < allTables.length; i++){
        allTables[i].addEventListener("click", async () => {
            // isolating the table name from id
            let table = allTables[i].id.replace("-table", "");
            // adding #<tablename> to the url path
            let url = new URL(document.URL);
            if(url.search.length === 0){
                url.searchParams.append("table", table);
            }
            else{
                url.searchParams.set("table", table);
            }
            window.history.pushState("", "", url);
            // getting table data
            let tableData = await fetchTable(table);
            // closing all tables
            let all_tables = document.getElementsByTagName("table");
            for(let i = 0; i< all_tables.length; i++){
                if(all_tables[i].id !== `${table}-table`){
                    all_tables[i].hidden = true;
                    all_tables[i].setAttribute("data-collapsed", "true");
                }
            }
            // creating the db table's table
            createTable(tableData);
        });
    }
});