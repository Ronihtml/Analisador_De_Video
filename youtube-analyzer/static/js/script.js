document.addEventListener("DOMContentLoaded", () => {
  // Elementos do DOM
  const form = document.getElementById("analyzer-form")
  const urlInput = document.getElementById("youtube-url")
  const analyzeButton = document.getElementById("analyze-button")
  const buttonText = analyzeButton.querySelector(".button-text")
  const spinner = analyzeButton.querySelector(".spinner")
  const progressContainer = document.getElementById("progress-container")
  const steps = document.querySelectorAll(".step")
  const errorContainer = document.getElementById("error-container")
  const errorMessage = document.getElementById("error-message")
  const summaryContainer = document.getElementById("summary-container")
  const summaryContent = document.getElementById("summary-content")
  const copyButton = document.getElementById("copy-button")
  const toast = document.getElementById("toast")

  // Função para mostrar o toast
  function showToast(message) {
    const toastMessage = document.querySelector(".toast-message")
    toastMessage.textContent = message
    toast.classList.remove("hidden")

    setTimeout(() => {
      toast.classList.add("hidden")
    }, 3000)
  }

  // Função para atualizar o estado dos passos
  function updateStepStatus(currentStep) {
    steps.forEach((step, index) => {
      step.classList.remove("active", "completed")

      if (index < currentStep) {
        step.classList.add("completed")
      } else if (index === currentStep) {
        step.classList.add("active")
      }
    })
  }

  // Função para resetar a interface
  function resetUI() {
    progressContainer.classList.add("hidden")
    errorContainer.classList.add("hidden")
    summaryContainer.classList.add("hidden")
    buttonText.textContent = "Analisar Vídeo"
    spinner.classList.add("hidden")
    analyzeButton.disabled = false
  }

  // Função para mostrar erro
  function showError(message) {
    errorContainer.classList.remove("hidden")
    errorMessage.textContent = message
  }

  // Função para processar a resposta do servidor
  async function processServerResponse(response) {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split("\n").filter((line) => line.trim())

      for (const line of lines) {
        try {
          const data = JSON.parse(line)

          if (data.step !== undefined) {
            updateStepStatus(data.step)
          }

          if (data.summary) {
            summaryContent.textContent = data.summary
            summaryContainer.classList.remove("hidden")

            // Marcar todos os passos como concluídos quando o resumo é recebido
            updateStepStatus(3) // Isso fará com que todos os passos (0, 1, 2) sejam marcados como concluídos

            // Adicionar link para ver detalhes da análise se tiver ID
            if (data.analise_id) {
              const summaryHeader = document.querySelector(".summary-header")
              if (summaryHeader && !document.getElementById("view-details-btn")) {
                const viewDetailsBtn = document.createElement("a")
                viewDetailsBtn.id = "view-details-btn"
                viewDetailsBtn.href = `/analise/${data.analise_id}`
                viewDetailsBtn.className = "btn-view"
                viewDetailsBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> Ver Detalhes'
                summaryHeader.appendChild(viewDetailsBtn)
              }
            }
          }

          if (data.error) {
            throw new Error(data.error)
          }
        } catch (e) {
          // Não é JSON ou outro erro, ignorar
        }
      }
    }
  }

  // Event listener para o formulário
  form.addEventListener("submit", async (e) => {
    e.preventDefault()

    const url = urlInput.value.trim()

    if (!url) {
      showError("Por favor, digite uma URL do YouTube")
      return
    }

    if (!url.includes("youtube.com") && !url.includes("youtu.be")) {
      showError("Por favor, digite uma URL válida do YouTube")
      return
    }

    // Resetar UI e mostrar progresso
    resetUI()
    buttonText.textContent = "Processando"
    spinner.classList.remove("hidden")
    analyzeButton.disabled = true
    progressContainer.classList.remove("hidden")
    updateStepStatus(0)

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Falha ao analisar o vídeo")
      }

      await processServerResponse(response)

      // Finalizar UI
      buttonText.textContent = "Analisar Vídeo"
      spinner.classList.add("hidden")
      analyzeButton.disabled = false
    } catch (err) {
      resetUI()
      showError(err.message || "Ocorreu um erro")
    }
  })

  // Event listener para o botão de copiar
  if (copyButton) {
    copyButton.addEventListener("click", () => {
      const text = summaryContent ? summaryContent.textContent : copyButton.getAttribute("data-text")
      navigator.clipboard
        .writeText(text)
        .then(() => {
          showToast("Copiado para a área de transferência!")
        })
        .catch((err) => {
          showToast("Erro ao copiar texto")
          console.error("Erro ao copiar: ", err)
        })
    })
  }
})
