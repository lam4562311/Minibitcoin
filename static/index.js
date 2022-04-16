let get_chain_bt = document.querySelector("#get_chain_bt");
let get_node_bt = document.querySelector("#get_node_bt");
let get_diff_info_bt = document.querySelector("#get_diff_info_bt");

let full_chain_span = document.querySelector("#fullchain_span");
let full_node_span = document.querySelector("#node_list_span");
let hostname_span = document.querySelector("#hostname_span");
let client_id_span = document.querySelector("#client_id_span");
let register_node_span = document.querySelector("#register_node_span");
let Register_node_submit_listener = document.getElementById("Register_form").addEventListener("submit", formSubmit);
let transaction_submit_span = document.querySelector("#transaction_submit_span");
let transaction_submit_listener = document.getElementById("transaction_form").addEventListener("submit", transactionSubmit);
let status_span = document.querySelector("#status_span");
let publickey_span = document.querySelector("#publickey_span");
let mining_result_span = document.querySelector("#mining_result");
let diff_info_span = document.querySelector("#diff_info_span");
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
    input = $('#Register_form').serializeArray();
    if(input[1].value!=""){
        if (confirm("You are doing Type B node registration which uses com_port, are you sure? \n"
            + "The recommended way to register a node is filing only the host field in the host:port format to do Type A node registration."))
        {
            $.ajax({
                url : "/register_node",
                type: 'post',
                data:{
                    "node": input[0].value,
                    "com_port": input[1].value
            },
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
    }else{
        $.ajax({
            url : "/register_node",
            type: 'post',
            data:{
                "node": input[0].value
        },
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
}

function transactionSubmit(event) {
    event.preventDefault();
    $.ajax({
        url : "/new_transaction",
        type: 'post',
        data:$('#transaction_form').serialize(),
        statusCode: {
            406: function(response) {
                alert(JSON.parse(response.responseText).message);
            },
            201: function(response) {
                transaction_submit_span.innerHTML = JSON.stringify(response.message);
            },
            400: function(response) {
                alert(JSON.stringify(response));
            },
            500: function(response) {
                alert("error");
            }
        },
        
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
            $.ajax({
                type: "PUT",
                url: "/update_balance",
                success: (data1) => {
                    alert(JSON.stringify(data1));
                }
            });
        }
    });
}

function get_diff_info(event){
    $.ajax({
        url: '/difficulty_info',
        type: "GET",
        contentType: "application/json; charset: utf-8",
        dataType: "json",
        success: (data) => {
            diff_info_span.innerHTML = JSON.stringify(data);
        }
    })
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
$(show_publickey).click(() => $("#publickey_span").toggle());
$("#show_manage_privkey").click(() => $("#manage_privatekey").toggle());
$(mining_bt).click(()=>mining());
$(get_diff_info_bt).click(()=>get_diff_info());
$(generate_new_wallet_bt).click(()=>generate_new_wallet());

setInterval(() => get_status(), 1000); // constantly refreshing balance