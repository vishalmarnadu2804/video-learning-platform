/**
 * Video Learning Platform - Client-side JavaScript
 * Handles AJAX lesson completion toggle, client validation, navigation, and toast alerts.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Navigation Toggle
  const mobileToggle = document.getElementById("mobileToggle");
  const navMenu = document.getElementById("navMenu");

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", function () {
      navMenu.classList.toggle("open");
      const isExpanded = navMenu.classList.contains("open");
      mobileToggle.setAttribute("aria-expanded", isExpanded);
    });
  }

  // 2. Mark as Completed AJAX Handler
  const toggleBtn = document.getElementById("btnToggleComplete");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", async function (e) {
      e.preventDefault();

      const lessonNumber = this.getAttribute("data-lesson-number");
      if (!lessonNumber) return;

      // Visual loading state
      const originalHtml = this.innerHTML;
      this.disabled = true;
      this.innerHTML = "Updating...";

      try {
        const response = await fetch(`/api/lesson/${lessonNumber}/toggle`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          }
        });

        if (response.status === 401) {
          // Unauthenticated session, redirect to login
          window.location.href = `/login?next=/lesson/${lessonNumber}`;
          return;
        }

        if (!response.ok) {
          throw new Error("Server responded with status " + response.status);
        }

        const data = await response.json();

        if (data.success) {
          updateLessonUI(data.is_completed, data.progress_pct, data.completed_count, data.total_count);
        } else {
          alert("Error: " + (data.error || "Could not update lesson progress"));
          this.innerHTML = originalHtml;
        }
      } catch (err) {
        console.error("AJAX error updating progress:", err);
        // Fallback: Submit standard POST form if available
        const fallbackForm = document.getElementById("fallbackCompleteForm");
        if (fallbackForm) {
          fallbackForm.submit();
        } else {
          alert("Network error: Could not connect to the server.");
          this.innerHTML = originalHtml;
        }
      } finally {
        this.disabled = false;
      }
    });
  }

  function updateLessonUI(isCompleted, progressPct, completedCount, totalCount) {
    const btn = document.getElementById("btnToggleComplete");
    const badge = document.getElementById("lessonStatusBadge");
    const lessonNum = btn.getAttribute("data-lesson-number");
    const sidebarItem = document.querySelector(`.playlist-item[data-lesson-number="${lessonNum}"]`);

    if (isCompleted) {
      // Completed state
      btn.className = "btn btn-success";
      btn.innerHTML = `<span class="icon">✓</span> Completed`;
      btn.setAttribute("title", "Click to mark as incomplete");

      if (badge) {
        badge.className = "status-badge completed";
        badge.textContent = "✓ Completed";
      }

      if (sidebarItem) {
        sidebarItem.classList.add("completed");
        const orderIcon = sidebarItem.querySelector(".playlist-order");
        if (orderIcon) orderIcon.textContent = "✓";
      }

      showToast(`Lesson ${lessonNum} completed! Total progress: ${completedCount}/${totalCount} (${progressPct}%).`);
    } else {
      // Incomplete state
      btn.className = "btn btn-outline-primary";
      btn.innerHTML = `Mark as Completed`;
      btn.setAttribute("title", "Click to mark as completed");

      if (badge) {
        badge.className = "status-badge incomplete";
        badge.textContent = "Not Completed";
      }

      if (sidebarItem) {
        sidebarItem.classList.remove("completed");
        const orderIcon = sidebarItem.querySelector(".playlist-order");
        if (orderIcon) orderIcon.textContent = lessonNum;
      }

      showToast(`Lesson ${lessonNum} unmarked. Total progress: ${completedCount}/${totalCount} (${progressPct}%).`);
    }
  }

  // 3. Client-side Sign Up Password Match Validation
  const signupForm = document.getElementById("signupForm");
  const pwdInput = document.getElementById("password");
  const confirmPwdInput = document.getElementById("confirm_password");
  const mismatchHint = document.getElementById("passwordMismatchHint");

  if (signupForm && pwdInput && confirmPwdInput) {
    function checkPasswordsMatch() {
      if (confirmPwdInput.value && pwdInput.value !== confirmPwdInput.value) {
        if (mismatchHint) mismatchHint.style.display = "block";
        confirmPwdInput.style.borderColor = "#ef4444";
        return false;
      } else {
        if (mismatchHint) mismatchHint.style.display = "none";
        confirmPwdInput.style.borderColor = "";
        return true;
      }
    }

    confirmPwdInput.addEventListener("input", checkPasswordsMatch);
    pwdInput.addEventListener("input", checkPasswordsMatch);

    signupForm.addEventListener("submit", function (e) {
      if (!checkPasswordsMatch()) {
        e.preventDefault();
        confirmPwdInput.focus();
      }
    });
  }

  // 4. Lightweight Toast Notification Helper
  function showToast(message) {
    let toast = document.getElementById("dynamicToast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "dynamicToast";
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background-color: #0f172a;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.18);
        font-size: 0.92rem;
        font-weight: 500;
        z-index: 9999;
        transition: opacity 0.3s ease, transform 0.3s ease;
        opacity: 0;
        transform: translateY(10px);
        max-width: 360px;
        line-height: 1.4;
      `;
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
    }, 3500);
  }
});
