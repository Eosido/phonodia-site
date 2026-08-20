
(function(){
  var hdr=document.getElementById('lc_page_header');
  var isCust=hdr&&hdr.classList.contains('cust_page_menu_style');
  function onScroll(){ if(!hdr) return; if(window.scrollY>120){hdr.classList.add('sticky_enabled');} else {hdr.classList.remove('sticky_enabled');} }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  // mobile menu
  var burger=document.querySelector('.hmb_menu'); var mnav=document.querySelector('.mobile_navigation_container');
  if(burger&&mnav){burger.addEventListener('click',function(){mnav.classList.toggle('open');});}
  // js links
  document.querySelectorAll('.lc_js_link[data-href]').forEach(function(el){
    el.addEventListener('click',function(e){var h=el.getAttribute('data-href'); if(!h||h=='#') return; if(el.getAttribute('data-target')=='_blank'){window.open(h,'_blank');} else {window.location.href=h;}});
  });
  // hero video popup
  document.querySelectorAll('.video_play_btn_scd[data-vid]').forEach(function(btn){
    btn.style.cursor='pointer'; var wrap=btn.closest('.swp_video_btn_scd')||btn; wrap.style.cursor='pointer';
    wrap.addEventListener('click',function(){
      var id=btn.getAttribute('data-vid');
      if(location.protocol==='file:'){ window.open('https://www.youtube.com/watch?v='+id,'_blank'); return; }
      var m=document.getElementById('swp_video_modal');
      if(!m){m=document.createElement('div');m.id='swp_video_modal';m.className='swp_video_modal';m.innerHTML='<span class="close">&times;</span><iframe allow="autoplay; fullscreen" allowfullscreen></iframe>';document.body.appendChild(m);
        m.querySelector('.close').addEventListener('click',function(){m.classList.remove('open');m.querySelector('iframe').src='';});
        m.addEventListener('click',function(e){if(e.target===m){m.classList.remove('open');m.querySelector('iframe').src='';}});}
      m.querySelector('iframe').src='https://www.youtube.com/embed/'+id+'?autoplay=1&rel=0';
      m.classList.add('open');
    });
  });
  // gallery lightbox (simple)
  document.querySelectorAll('a[data-lightbox]').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();
      var m=document.getElementById('swp_img_modal');
      if(!m){m=document.createElement('div');m.id='swp_img_modal';m.className='swp_video_modal';m.innerHTML='<span class="close">&times;</span><img style="max-width:92vw;max-height:90vh;object-fit:contain">';document.body.appendChild(m);
        m.querySelector('.close').addEventListener('click',function(){m.classList.remove('open');});
        m.addEventListener('click',function(e){if(e.target===m){m.classList.remove('open');}});}
      m.querySelector('img').src=a.getAttribute('href'); m.classList.add('open');
    });
  });
  // hero video autoplay
  var v=document.querySelector('#hero video.hero-video'); if(v){v.muted=true;v.play&&v.play().catch(function(){});}
})();

(function(){
  var KEY='fonodia_cart_v1', mem=[];
  function read(){ try{ var s=localStorage.getItem(KEY); return s?JSON.parse(s):[]; }catch(e){ return mem; } }
  function write(v){ mem=v; try{ localStorage.setItem(KEY,JSON.stringify(v)); }catch(e){} badge(); }
  function count(){ return read().reduce(function(n,i){return n+i.q;},0); }
  function money(c){ return (c/100).toFixed(2).replace('.',',')+' €'; }
  function badge(){ document.querySelectorAll('.cart-contents-count').forEach(function(el){ el.textContent=count(); }); }
  badge();

  // ---- product page
  var pp=document.querySelector('.single_product');
  if(pp){
    var sel={size:null,color:null};
    function pick(group,btn){ pp.querySelectorAll('#'+group+' .opt').forEach(function(b){b.classList.remove('sel');});
      btn.classList.add('sel'); sel[group==='sizes'?'size':'color']=btn.getAttribute('data-v');
      if(group==='colors'){ var lbl=pp.querySelector('#color_pick');
        if(lbl) lbl.textContent=btn.getAttribute('data-v');
        var vi=btn.getAttribute('data-img'), im=pp.querySelector('#prod_main_img');
        if(vi&&im){ im.src=vi; pp.dataset.pimg=vi; }
        var vf=btn.getAttribute('data-full'), zl=pp.querySelector('#prod_zoom');
        if(vf&&zl){ zl.setAttribute('href',vf); } }
      check(); }
    pp.querySelectorAll('#sizes .opt').forEach(function(b){ b.onclick=function(){pick('sizes',b);}; });
    pp.querySelectorAll('#colors .opt').forEach(function(b){ b.onclick=function(){pick('colors',b);}; });
    var one=pp.querySelectorAll('#colors .opt'); if(one.length===1) pick('colors',one[0]);
    var qty=pp.querySelector('#qty'), btnA=pp.querySelector('#add_to_cart'), msg=pp.querySelector('#add_msg');
    pp.querySelector('.qminus').onclick=function(){ qty.value=Math.max(1,(parseInt(qty.value)||1)-1); };
    pp.querySelector('.qplus').onclick=function(){ qty.value=Math.min(99,(parseInt(qty.value)||1)+1); };
    function need(){ return (pp.querySelectorAll('#sizes .opt').length&&!sel.size) || (pp.querySelectorAll('#colors .opt').length&&!sel.color); }
    function check(){ btnA.disabled=need(); }
    check();
    btnA.onclick=function(){
      if(need()) return;
      var it={id:pp.dataset.pid, name:pp.dataset.pname, price:parseInt(pp.dataset.pprice),
              img:pp.dataset.pimg, url:pp.dataset.purl, size:sel.size, color:sel.color,
              q:Math.max(1,parseInt(qty.value)||1)};
      var c=read(), k=c.find(function(x){return x.id===it.id&&x.size===it.size&&x.color===it.color;});
      if(k) k.q+=it.q; else c.push(it);
      write(c);
      msg.textContent=btnA.getAttribute('data-added')||msg.getAttribute('data-added')||'';
      msg.textContent=pp.getAttribute('data-added')||'✓';
      msg.textContent='✓ '+(document.body.lang==='en'?'Added to your basket':'Προστέθηκε στο καλάθι');
    };
  }

  // ---- order page
  var op=document.querySelector('.order_page');
  if(op){
    var SHIP=JSON.parse(op.dataset.ship), MAXQ=parseInt(op.dataset.max,10);
    var oc=op.querySelector('#order_cart');
    var zone=op.querySelector('#of_zone'), meths=op.querySelector('#dl_methods');
    var boxWrap=op.querySelector('#dl_locker'), addrWrap=op.querySelector('#dl_addr');
    var hasBox=!!meths;   // όσο δεν έχουμε λογαριασμό BOX NOW, δεν υπάρχουν καν τα κουτιά
    var shipBox=op.querySelector('#ship_box');
    var form=op.querySelector('#order_form'), omsg=op.querySelector('#of_msg');

    function itemsTotal(){ var t=0; read().forEach(function(it){ t+=it.price*it.q; }); return t; }
    function itemsCount(){ var n=0; read().forEach(function(it){ n+=it.q; }); return n; }
    function method(){ if(!hasBox) return 'door';
      var r=op.querySelector('input[name=dl]:checked'); return r?r.value:'door'; }

    // Πόσο κοστίζει η αποστολή· null σημαίνει «θα το πούμε μαζί».
    function shipCost(){
      var z=zone.value, n=itemsCount(), tiers=SHIP[z];
      if(!tiers||!n) return null;
      for(var i=0;i<tiers.length;i++){ if(n<=tiers[i][0]) return tiers[i][1]; }
      return null;
    }

    function renderCart(){
      var c=read();
      if(!c.length){ oc.innerHTML='<p class="cart_empty">'+op.dataset.empty+'</p>'; return; }
      var rows='';
      c.forEach(function(it){
        var v=[it.size,it.color].filter(Boolean).join(' · ');
        rows+='<tr><td class="ct_img"><img src="'+it.img+'" alt=""></td>'+
          '<td><span class="ct_name">'+it.name+'</span><span class="ct_var">'+v+'</span></td>'+
          '<td class="ct_price">'+money(it.price)+' × '+it.q+'</td>'+
          '<td class="ct_sum">'+money(it.price*it.q)+'</td></tr>';
      });
      oc.innerHTML='<table class="cart_table"><tbody>'+rows+'</tbody></table>';
    }

    function sync(){
      var gr=zone.value==='gr', box=false;
      if(hasBox){
        // Οι θυρίδες BOX NOW υπάρχουν μόνο στην Ελλάδα. Έξω, μόνο στην πόρτα.
        meths.classList.toggle('hide',!gr);
        if(!gr){ op.querySelector('input[name=dl][value=door]').checked=true; }
        box=gr&&method()==='box';
        boxWrap.classList.toggle('hide',!box);
      }
      addrWrap.classList.toggle('hide',box);

      var items=itemsTotal(), sc=shipCost(), n=itemsCount();
      var html='<div class="ship_line"><span>'+op.dataset.items+'</span><span>'+money(items)+'</span></div>';
      html+='<div class="ship_line"><span>'+op.dataset.shiph+'</span><span>'+
            (sc===null?op.dataset.ask:money(sc))+'</span></div>';
      html+='<div class="ship_line grand"><span>'+op.dataset.grand+'</span><b>'+
            (sc===null?money(items)+' + '+op.dataset.ask:money(items+sc))+'</b></div>';
      if(sc===null&&n){ html+='<p class="ship_warn">'+
        (zone.value==='ww'?op.dataset.ww:op.dataset.big)+'</p>'; }
      shipBox.innerHTML=html;
    }

    renderCart(); sync();
    zone.onchange=sync;
    op.querySelectorAll('input[name=dl]').forEach(function(r){ r.onchange=sync; });

    form.onsubmit=function(e){
      e.preventDefault();
      var cart=read();
      if(!cart.length){ omsg.textContent=op.dataset.empty; return; }
      var need=['of_name','of_email','of_phone'];
      var box=hasBox&&zone.value==='gr'&&method()==='box';
      if(box){ need.push('of_locker'); } else { need=need.concat(['of_addr','of_city','of_zip']); }
      var vals={}, ok=true;
      ['of_name','of_email','of_phone','of_addr','of_city','of_zip','of_locker'].forEach(function(id){
        var el=op.querySelector('#'+id); if(!el) return;
        var v=(el.value||'').trim(); vals[id]=v;
        var must=need.indexOf(id)>=0;
        if(must&&!v){ el.classList.add('bad'); ok=false; } else { el.classList.remove('bad'); }
      });
      if(!ok){ omsg.textContent=op.dataset.req; return; }
      vals.of_notes=(op.querySelector('#of_notes').value||'').trim();

      var lines=[], tot=0;
      cart.forEach(function(it){
        var sum=it.price*it.q; tot+=sum;
        lines.push('- '+it.name+' | '+[it.size,it.color].filter(Boolean).join(' / ')+
                   ' | x'+it.q+' | '+money(sum));
      });
      var sc=shipCost();
      var zt=zone.options[zone.selectedIndex].text;
      var how=box?(op.querySelector('label.dl_m b').textContent+': '+vals.of_locker)
                 :(vals.of_addr+', '+vals.of_city+' '+vals.of_zip);
      if(!hasBox){ how=vals.of_addr+', '+vals.of_city+' '+vals.of_zip; }
      var body=[op.dataset.subject,'',lines.join('\n'),'',
        op.dataset.items+': '+money(tot),
        op.dataset.shiph+': '+(sc===null?op.dataset.ask:money(sc)),
        op.dataset.grand+': '+(sc===null?money(tot)+' + '+op.dataset.ask:money(tot+sc)),'',
        '---','',
        vals.of_name,vals.of_email,vals.of_phone,'',
        zt,how,
        vals.of_notes?('\n'+vals.of_notes):''].join('\n');

      var ep=op.dataset.endpoint;
      if(ep){
        var fd=new FormData();
        fd.append('subject',op.dataset.subject); fd.append('message',body);
        fd.append('email',vals.of_email); fd.append('name',vals.of_name);
        fetch(ep,{method:'POST',body:fd}).then(function(){ omsg.textContent=op.dataset.ok; });
        return;
      }
      var href='mailto:'+op.dataset.to+'?cc='+op.dataset.cc+
               '&subject='+encodeURIComponent(op.dataset.subject)+
               '&body='+encodeURIComponent(body);
      omsg.textContent=op.dataset.ok;
      window.location.href=href;
    };
  }

  // ---- cart page
  var cp=document.querySelector('.cart_page');
  if(cp){
    function render(){
      var c=read(), box=cp.querySelector('#cart_body');
      if(!c.length){ box.innerHTML='<p class="cart_empty">'+cp.dataset.empty+'</p>'; return; }
      var rows='', total=0;
      c.forEach(function(it,i){
        var sum=it.price*it.q; total+=sum;
        var v=[it.size,it.color].filter(Boolean).join(' · ');
        rows+='<tr><td class="ct_img"><img src="'+it.img+'" alt=""></td>'+
          '<td><span class="ct_name">'+it.name+'</span><span class="ct_var">'+v+'</span></td>'+
          '<td class="ct_price">'+money(it.price)+' × '+it.q+'</td>'+
          '<td class="ct_sum">'+money(sum)+'<button class="ct_rm" data-i="'+i+'" title="'+cp.dataset.remove+'">×</button></td></tr>';
      });
      box.innerHTML='<table class="cart_table"><tbody>'+rows+'</tbody></table>'+
        '<div class="cart_total"><span>'+cp.dataset.total+'</span><b>'+money(total)+'</b></div>'+
        '<div class="cart_actions"><a class="checkout_btn" href="'+cp.dataset.wc+'">'+cp.dataset.checkout+'</a></div>';
      box.querySelectorAll('.ct_rm').forEach(function(b){ b.onclick=function(){ var c=read(); c.splice(parseInt(b.dataset.i),1); write(c); render(); }; });
    }
    render();
  }
})();
