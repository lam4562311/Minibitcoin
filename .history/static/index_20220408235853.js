let get_chain_bt = document.querySelector("#get_chain_bt");
let get_node_bt = document.querySelector("#get_node_bt");

let full_chain_span = document.querySelector("#fullchain_span")
let full_node_span = document.querySelector("#node_list_span")
let hostname_span = document.querySelector("#hostname_span")
let client_id_span = document.querySelector("#client_id_span")

hostname_span.innerHTML = window.location.hostname;
client_id_span.innerHTML = window.location.port;

function get_full_chain(){
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=utf-8",
        url:"/fullchain",
        dataType: "json",
        success: (data) => {
            full_chain_span.innerHTML = JSON.stringify(data);
        }
    });
    querystring = window.location.search;
}

function get_node_list(){
    $.ajax(
        {
            type: "GET",
            contentType: "application/json; charset: utf-8",
            url:"/get_nodes",
            dataType: "json",
            success: (data) => {
                full_node_span.innerHTML = JSON.stringify(data);
            } 
        }
    )
}

$(get_chain_bt).click(()=>get_full_chain());
$(get_node_bt).click(()=>get_node_list());