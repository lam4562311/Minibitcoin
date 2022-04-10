let get_chain_bt = document.querySelector("#get_chain_bt");
let get_node_bt = document.querySelector("#get_node_bt");

let full_chain_span = document.querySelector("#fullchain_span")
let full_node_span = document.querySelector("#node_list_span")
let hostname_span = document.querySelector("#hostname_span")
let client_id_span = document.querySelector("#client_id_span")
let register_node_span = document.querySelector("#register_node_span")
let Register_node_submit_listener = document.getElementById("Register_form").addEventListener("submit", formSubmit)
let transaction_submit_span = document.querySelector("#transaction_submit_span")
let transaction_submit_listener = document.getElementById("transaction_form").addEventListener("submit", transactionSubmit)
let status_span = document.querySelector("#status_span")
let publickey_span = document.querySelector("#publickey_span")
let mining_result_span = document.querySelector("#mining_result")

let generate_new_wallet_bt = document.querySelector("#generate_new_wallet_bt");

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
            type: "get",
            contentType: "application/json; charset: utf-8",
            url:"/get_nodes",
            dataType: "json",
            success: (data) => {
                full_node_span.innerHTML = "Clients: "+JSON.stringify(data.nodes);
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
                status_span.innerHTML = "Balance: "+JSON.stringify(data.balance);
                publickey_span.innerHTML = "Public Key: \n"+JSON.stringify(data.public_key);
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
            200: function(response) {
                register_node_span.innerHTML = JSON.stringify(response);
            },
            201: function(response) {
                alert(JSON.stringify(response.message));
                register_node_span.innerHTML = "Total node: "+JSON.stringify(response.total_nodes);
            },
            400: function(response) {
                alert(JSON.stringify(response.message));
                register_node_span.innerHTML = "Total node: "+JSON.stringify(response.total_nodes);
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
                transaction_submit_span.innerHTML = JSON.stringify(response.message);
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

function mining(event){
    $.ajax({
        url: '/mine',
        type :'get',
        contentType: "application/json; charset: utf-8",
        dataType: 'json',
        success: (data) => {
            mining_result_span.innerHTML = JSON.stringify(data);
        }
    });
}

function generate_new_wallet(){
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url:"/generate_new_wallet",
        success: (data) => {
            alert("new wallet identity is generated");
        }
    });
}

$(get_chain_bt).click(()=>get_full_chain());
$(get_node_bt).click(()=>get_node_list());
$(get_status_bt).click(()=>get_status());
$(show_publickey).click(()=>{var x = document.getElementById("publickey_div").style.display;
                                if(x==="none")
                                {
                                    document.getElementById("publickey_div").style.display = "block";
                                }else{
                                    document.getElementById("publickey_div").style.display = "none";
                                }});
$(mining_bt).click(()=>mining());
$(generate_new_wallet_bt).click(()=>generate_new_wallet());