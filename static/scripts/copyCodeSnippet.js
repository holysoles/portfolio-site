async function copyCodeSnippet(code_id) {
  const code = document.getElementById(code_id).getElementsByTagName('code')[0].innerText;
  await navigator.clipboard.writeText(code);
}