document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("dnd-area");
    const fileInput = document.getElementById("file-input");
    const fileListDiv = document.getElementById("dnd-file-list");
    const maxFiles = 5;

    function updateFileList() {
        fileListDiv.innerHTML = "";
        const selectedFiles = Array.from(fileInput.files);

        selectedFiles.forEach((file, index) => {
            let fileDiv = document.createElement("div");
            fileDiv.className = "alert alert-secondary d-flex justify-content-between align-items-center";
            fileDiv.innerHTML = `
                ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                <button type="button" class="btn-close" data-index="${index}" aria-label="Remove"></button>
            `;

            fileDiv.querySelector(".btn-close").addEventListener("click", function () {
                removeFile(index);
            });

            fileListDiv.appendChild(fileDiv);
        });

        // Check max file limit
        if (selectedFiles.length > maxFiles) {
            alert(`You can only upload up to ${maxFiles} files.`);
            fileInput.value = "";
            fileListDiv.innerHTML = "";
        }
    }

    function removeFile(index) {
        const dataTransfer = new DataTransfer();
        const files = Array.from(fileInput.files);
        files.forEach((file, i) => {
            if (i !== index) {
                dataTransfer.items.add(file);
            }
        });
        fileInput.files = dataTransfer.files;

        updateFileList();
    }

    function handleFiles(files) {
        const dataTransfer = new DataTransfer();
        const currentFiles = Array.from(fileInput.files);
        
        const allFiles = currentFiles.concat(Array.from(files));

        if (allFiles.length > maxFiles) {
            alert(`You can only upload up to ${maxFiles} files.`);
            return;
        }

        allFiles.forEach((file) => {
            dataTransfer.items.add(file);
        });

        fileInput.files = dataTransfer.files;

        updateFileList();
    }

    // Drag-and-drop functionality
    dropArea.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropArea.classList.add("bg-success-subtle", "text-primary-emphasis");
    });
    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("bg-success-subtle", "text-primary-emphasis");
    });
    dropArea.addEventListener("drop", (event) => {
        event.preventDefault();
        dropArea.classList.remove("bg-success-subtle", "text-primary-emphasis");
        handleFiles(event.dataTransfer.files);
    });

    fileInput.addEventListener("change", updateFileList);
});
