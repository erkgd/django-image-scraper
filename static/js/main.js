// Main JavaScript file for the Image Scraper application

document.addEventListener("DOMContentLoaded", () => {
  // Initialize image lazy loading
  const lazyImages = document.querySelectorAll(".lazy-load")

  if ("IntersectionObserver" in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target
          img.src = img.dataset.src
          img.classList.remove("lazy-load")
          imageObserver.unobserve(img)
        }
      })
    })

    lazyImages.forEach((img) => {
      imageObserver.observe(img)
    })
  } else {
    // Fallback for browsers that don't support IntersectionObserver
    lazyImages.forEach((img) => {
      img.src = img.dataset.src
    })
  }

  // Handle image search form submission
  const searchForm = document.getElementById("search-form")
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      const searchInput = document.getElementById("id_query")
      if (!searchInput.value.trim()) {
        e.preventDefault()
        showNotification("Please enter a search query", "error")
      }
    })
  }

  // Handle image like buttons
  const likeButtons = document.querySelectorAll(".like-button")
  likeButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault()

      const isAuthenticated = button.dataset.authenticated === "true"
      if (!isAuthenticated) {
        window.location.href = "/accounts/login/"
        return
      }

      const imageId = button.dataset.imageId
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content")

      fetch(`/image/${imageId}/like/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
        credentials: "same-origin",
      })
        .then((response) => response.json())
        .then((data) => {
          const likesCount = button.nextElementSibling
          likesCount.textContent = data.likes_count

          if (data.liked) {
            button.classList.add("text-red-500")
            button.querySelector("svg").setAttribute("fill", "currentColor")
          } else {
            button.classList.remove("text-red-500")
            button.querySelector("svg").setAttribute("fill", "none")
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          showNotification("An error occurred. Please try again.", "error")
        })
    })
  })

  // Notification system
  function showNotification(message, type = "info") {
    const notification = document.createElement("div")
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${type === "error" ? "bg-red-500" : "bg-green-500"} text-white max-w-xs z-50`
    notification.textContent = message

    document.body.appendChild(notification)

    setTimeout(() => {
      notification.classList.add("opacity-0", "transition-opacity", "duration-500")
      setTimeout(() => {
        document.body.removeChild(notification)
      }, 500)
    }, 3000)
  }

  // Image preview modal
  const previewButtons = document.querySelectorAll(".preview-button")
  const previewModal = document.getElementById("preview-modal")
  const previewImage = document.getElementById("preview-image")
  const closeModal = document.getElementById("close-modal")

  if (previewButtons.length && previewModal) {
    previewButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const imageUrl = this.dataset.imageUrl
        const imageTitle = this.dataset.imageTitle

        previewImage.src = imageUrl
        previewImage.alt = imageTitle
        previewModal.classList.remove("hidden")
      })
    })

    closeModal.addEventListener("click", () => {
      previewModal.classList.add("hidden")
    })

    // Close modal when clicking outside the image
    previewModal.addEventListener("click", (e) => {
      if (e.target === previewModal) {
        previewModal.classList.add("hidden")
      }
    })

    // Close modal with Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !previewModal.classList.contains("hidden")) {
        previewModal.classList.add("hidden")
      }
    })
  }
})
