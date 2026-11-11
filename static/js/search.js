(function(){var q=document.getElementById('q'),c=document.getElementById('col'),l=document.getElementById('list');if(!q||!l)return;
var cards=[].slice.call(l.children),n=document.getElementById('count');
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
function run(){var t=norm(q.value.trim()),k=c.value,v=0;cards.forEach(function(e){var ok=(!t||e.dataset.q.indexOf(t)>-1)&&(!k||e.dataset.col===k);e.hidden=!ok;if(ok)v++});n.textContent=v+' titluri'}
q.addEventListener('input',run);c.addEventListener('change',run);run()})();
