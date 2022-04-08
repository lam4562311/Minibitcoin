let generate_wallet_bt = document.querySelector("#generate_wallet_bt");
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

$(generate_wallet_bt).click(()=>get_full_chain());