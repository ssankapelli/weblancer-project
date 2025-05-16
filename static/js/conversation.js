document.addEventListener("DOMContentLoaded", function () {
    const conversationItems = document.querySelectorAll('.conversation-list-items');
    const messagePanel = document.getElementById('chat-window');
    const messageList = document.getElementById('chat-box');
    // const goDownButton = document.getElementById('go-down-button');
    const messageForm = document.getElementById('message-form');
    const messageContentInput = document.getElementById('message-content');
    // const conversationIdInput = document.getElementById('conversation-id');

    const chatHeaderTitle = document.getElementById('chat-header-title');
    const chatHeaderProject = document.getElementById('chat-header-project');
    const chatHeaderProposal = document.getElementById('chat-header-proposal');
    let conversationId = null;

    function toggleSidebar() {
        console.log("asd");
        const conversationList = document.getElementById("conversation-list");
        conversationList.classList.toggle("d-none");
        if (window.innerWidth < 768) {
            if (!conversationList.classList.contains("d-none")) {
                conversationList.style.width = "100vw";
                messagePanel.classList.add("d-none");
            } else {
                conversationList.style.width = "";
                messagePanel.classList.remove("d-none");
            }
        }
    }

    document.getElementById("toggle-sidebar").addEventListener("click", toggleSidebar);
    
    conversationItems.forEach(item => {
        item.addEventListener('click', function () {
            // Remove active class from all items
            conversationItems.forEach(item => item.classList.remove('active'));
            // Add active class to the clicked item
            this.classList.add('active');

            // conversationId = this.getAttribute('data-conv-id');
            conversationId = this.dataset.convId;
            loadMessages(conversationId, true);
            messagePanel.classList.remove('d-none');
            messageForm.classList.remove('d-none');
            messageContentInput.focus();
            if (window.innerWidth < 768) {
                // document.getElementById('conversation-list').style.display = 'none';
                document.getElementById('conversation-list').classList.add('d-none');
                messagePanel.classList.add('d-none');
                messageContentInput.focus();
            }
        });
    });

    messageForm.addEventListener('submit', function (event) {
        event.preventDefault();
        // const conversationId = conversationIdInput.value;
        const content = messageContentInput.value.trim();
        console.log(conversationId, content);
        if (conversationId && content) {
            fetch(`/send_chat/${conversationId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': messageForm.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: new URLSearchParams({ content }).toString()
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('message-content').value = '';
                    loadMessages(conversationId);
                } else {
                    alert('Error sending message');
                }
            });
            messageContentInput.focus();
        }
    });

    function loadMessages(conversationId, update_header=false) {
        fetch(`/api/conversations/${conversationId}/messages/`)
            .then(response => response.json())
            .then(data => {
                if (update_header) {
                    chatHeaderTitle.innerText = data.project_title;
                    chatHeaderProject.href = chatHeaderProject.getAttribute("data-url").replace("0", data.project_id);
                    chatHeaderProposal.href = chatHeaderProposal.getAttribute("data-url").replace("0", data.proposal_id);
                }
                messagePanel.classList.remove('d-none');
                messageList.innerHTML = '';
                data.messages.forEach(message => {
                    const messageElement = document.createElement('div');
                    messageElement.classList.add('message');
                    if (message.recipient_id === data.current_user_id) {
                        messageElement.classList.add('message-sent');
                    } else {
                        messageElement.classList.add('message-received');
                    }
                    messageElement.innerHTML = `<strong>${message.sender_name}</strong>: ${message.content}`;
                    messageList.appendChild(messageElement);
                });
                scrollToBottom();
            });
    }

    // function getCookie(name) {
    //     let cookieValue = null;
    //     if (document.cookie && document.cookie !== "") {
    //         document.cookie.split(";").forEach(cookie => {
    //             let trimmed = cookie.trim();
    //             if (trimmed.startsWith(name + "=")) {
    //                 cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
    //             }
    //         });
    //     }
    //     return cookieValue;
    // }
    // Function to get CSRF token for AJAX requests
    // function getCSRFToken() {
    //     return document.cookie.split("; ")
    //         .find(row => row.startsWith("csrftoken"))
    //         ?.split("=")[1];
    // }
    // Function to poll for new messages every 4 seconds
    function pollNewMessages() {
        if (conversationId) {
            loadMessages(conversationId);
        }
        setTimeout(pollNewMessages, 4000);
    }
    pollNewMessages();
    function scrollToBottom() {
        messageList.scrollTop = messageList.scrollHeight;
    }

    document.getElementById("searchBtn").addEventListener("click", function() {
        let searchInput = document.getElementById("searchInput");
        searchInput.classList.toggle("d-none");
        searchInput.focus();
    });
    
});
