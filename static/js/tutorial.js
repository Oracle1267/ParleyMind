let tutorialStep = 0;
let noviceActive = false;

const steps = [
  {
    title: "Step 1: Safer Core",
    text: "Pick six strong favorites (around -300). These stabilize your parlay.",
  },
  {
    title: "Step 2: Solid Edges",
    text: "Add 3–4 spreads or totals near -110. This adds leverage with limited risk.",
  },
  {
    title: "Step 3: Value Pops",
    text: "Add 3 value legs (+150 to +250). These create your multiplier potential.",
  },
  {
    title: "Evaluation",
    text: "Let's check how your parlay stacks up...",
  },
];

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("noviceToggle").addEventListener("click", showGuide);
  document.getElementById("tutorial-next").addEventListener("click", nextStep);
  document.getElementById("copyParlay").addEventListener("click", copyParlaySummary);
});

function showGuide() {
  noviceActive = true;
  tutorialStep = 0;
  document.getElementById("tutorial-overlay").style.display = "flex";
  updateTutorial();
}

function nextStep() {
  tutorialStep++;
  if (tutorialStep >= steps.length) {
    analyzeParlay();
  } else {
    updateTutorial();
  }
}

function endGuide() {
  noviceActive = false;
  document.getElementById("tutorial-overlay").style.display = "none";
}

function updateTutorial() {
  const step = steps[tutorialStep];
  document.getElementById("tutorial-step-title").innerText = step.title;
  document.getElementById("tutorial-step-text").innerText = step.text;
  document.getElementById("tutorial-next").innerText = 
    tutorialStep === steps.length - 1 ? "Analyze" : "Next";
}

function analyzeParlay() {
  // Pull data from global parlay array
  const safe = parlay.filter(l => l.level === 1).length;
  const medium = parlay.filter(l => l.level === 2).length;
  const value = parlay.filter(l => l.level === 3).length;

  let message = "";
  if (safe >= 5 && medium >= 3 && value >= 2) {
    message = "✅ Balanced build. You’ve got a realistic parlay with layered risk.";
  } else if (value > 4) {
    message = "⚠️ Too many high-risk legs. Try adding more -200 to -300 favorites.";
  } else if (safe > 8 && value < 2) {
    message = "💤 Very safe, but low upside. Add a couple of +150 to +250 legs.";
  } else {
    message = "🧩 Needs adjustment. Aim for roughly 6 safe, 3 medium, 3 value legs.";
  }

  document.getElementById("tutorial-step-title").innerText = "Parlay Analysis";
  document.getElementById("tutorial-step-text").innerText = message;
  document.getElementById("tutorial-next").innerText = "Close";
  document.getElementById("tutorial-next").onclick = endGuide;
}

function copyParlaySummary() {
  const level1 = document.getElementById("level1-list").innerText.trim();
  const level2 = document.getElementById("level2-list").innerText.trim();
  const level3 = document.getElementById("level3-list").innerText.trim();
  const combined = document.getElementById("combined-odds").innerText;
  const payout = document.getElementById("payout").innerText;

  const summary = `
PARLAY BUILDER SUMMARY
======================
Level 1 – Safer Core:
${level1 || "(none)"}

Level 2 – Solid Edges:
${level2 || "(none)"}

Level 3 – Value Pops:
${level3 || "(none)"}

Combined Odds: ${combined}
Potential Payout: ${payout}
======================
  `;
  navigator.clipboard.writeText(summary);
  alert("Copied your parlay summary to clipboard!");
}
