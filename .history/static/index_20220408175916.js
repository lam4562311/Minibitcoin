let generate_wallet_bt = document.querySelector("#generate_wallet_bt");

function get_full_chain(){
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=utf-8",
        url:"/fullchain",
        dataType: "json",
    });
    
}

$(generate_wallet_bt).mouseclick(()=>get_full_chain());