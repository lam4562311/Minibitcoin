let get_chain_bt = document.querySelector("#get_chain_bt");
let get_node_bt = document.querySelector("#get_node_bt");

let full_chain_span = document.querySelector("#fullchain_span")
let full_node_span = document.querySelector("#node_list_span")
let hostname_span = document.querySelector("#hostname_span")
let client_id_span = document.querySelector("#client_id_span")
let register_node_span = document.querySelector("#register_node_span")
let Register_node_submit_listener = document.getElementById("Register_form").addEventListener("submit", formSubmit);
let transaction_submit_span = document.getElementById("#transcation_submit_span")
let transaction_submit_listener = document.getElementById("transaction_form").addEventListener("submit", transactionSubmit);
let status_span = document.querySelector("#status_span")
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
    );
}
function get_status(){
    $.ajax(
        {
            type: "GET",
            contentType: "application/json; charset: utf-8",
            url:"/get_status",
            dataType: "json",
            success: (data) => {
                status_span.innerHTML = JSON.stringify(data);
            } 
        }
    );
}
function formSubmit(event) {
    event.preventDefault();
    $.ajax({
        url : "/register_node",
        type: 'post',
        data:$('#Register_form').serialize(),
        statusCode: {
            201: function(response) {
                register_node_span.innerHTML = JSON.stringify(response);
            },
            200: function(response) {
                alert(JSON.stringify(response.message));
                register_node_span.innerHTML = "Total ndoe: "+JSON.stringify(response.total_nodes);
            },
            400: function(response) {
                alert(JSON.stringify(response.message));
                register_node_span.innerHTML = "Total ndoe: "+JSON.stringify(response.total_nodes);
            },
        }
    });
}

function transactionSubmit(event) {
    event.preventDefault();
    $.ajax({
        url : "/new_transaction",
        type: 'post',
        data:$('#transaction_form').serialize(),
        statusCode: {
            201: function(response) {
                register_node_span.innerHTML = JSON.stringify(response.message);
            },
            400: function(response) {
                alert(JSON.stringify(response));
            },
            406: function(response) {
                alert(JSON.stringify(response.message));
            },
        }
    });
}

$(get_chain_bt).click(()=>get_full_chain());
$(get_node_bt).click(()=>get_node_list());
$(get_status).click(()=>get_status());
