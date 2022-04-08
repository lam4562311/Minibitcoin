let get_chain_bt = document.querySelector("#get_chain_bt");
let get_node_bt = document.querySelector("#get_node_bt");

let sth_span = document.querySelector("#sth")

function get_full_chain(){
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=utf-8",
        url:"/fullchain",
        dataType: "json",
        success: (data) => {
            sth_span.innerHTML = JSON.stringify(data);
        }
    });
    
}

$(get_chain_bt).click(()=>get_full_chain());