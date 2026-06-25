#!/usr/bin/env node
/*
 * build-index.js — regenerates index.html for articles.phantom-byte.com
 *
 * Source of truth: articles-data.js (window.PB_ARTICLES, PB_AUTHORITY, PB_NETWORK)
 * Template:        index-template.html (has <!--FEATURED--> and <!--FEED--> markers)
 * Output:          index.html  (static, SEO-friendly: all article cards are real <a> links in HTML)
 *
 * Usage:  node build-index.js
 *
 * Workflow:
 *   - publish-article skill: prepend a new article object to articles-data.js, then run this.
 *   - edit-articles-page skill: edit index-template.html (design/CSS/sections), then run this.
 *
 * The generated index.html contains ALL article cards as static HTML so search
 * engines and no-JS users see every article link. The inline console enhancer
 * only does pagination / category filter / mobile dropdown by reading the DOM.
 */

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DATA_FILE = path.join(ROOT, 'articles-data.js');
const TEMPLATE_FILE = path.join(ROOT, 'index-template.html');
const OUT_FILE = path.join(ROOT, 'index.html');

// --- Load the data file (it assigns window.PB_ARTICLES etc.) ---
global.window = {};
require(DATA_FILE);
const articles = (window.PB_ARTICLES || []).slice();
const authority = (window.PB_AUTHORITY || []).slice();
// authority cards get an "external" flag so the markup/JS treats them as outbound
authority.forEach(a => a.external = true);

// --- HTML escaping ---
function escText(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escAttr(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// --- Card markup (static, SEO-friendly: real <a> links) ---
function panelCard(a) {
  const ext = !!a.external;
  const href = ext ? a.href : a.href;            // data file already holds relative slug.html / absolute URL
  const cls = 'panel' + (ext ? ' ext' : '');
  const idx = ext ? '<span class="pidx">★</span>' : '<span class="pidx">#' + a.n + '</span>';
  const linkAttr = ext ? ' target="_blank" rel="nofollow noopener"' : ' rel="noopener"';
  return ''
    + '<article class="' + cls + '" data-cat="' + escAttr(a.cat) + '" data-href="' + escAttr(href) + '" data-external="' + (ext ? 1 : 0) + '">'
    +   '<div class="thumb">'
    +     '<img loading="lazy" src="' + escAttr(a.img) + '" alt="' + escAttr(a.title) + '">'
    +     '<span class="pcat">' + escText(a.cat) + '</span>' + idx
    +   '</div>'
    +   '<div class="pbody">'
    +     '<h3><a href="' + escAttr(href) + '"' + linkAttr + '>' + escText(a.title) + '</a></h3>'
    +     '<p class="pexc">' + escText(a.excerpt) + '</p>'
    +     '<div class="pmeta"><span class="pw">' + escText(a.author) + '</span><span class="pd">' + escText(a.date) + '</span></div>'
    +   '</div>'
    + '</article>';
}

function featuredCard(a) {
  const href = a.href;
  return ''
    + '<div class="featured" data-href="' + escAttr(href) + '">'
    +   '<div class="feat-img"><img src="' + escAttr(a.img) + '" alt="' + escAttr(a.title) + '"><span class="feat-badge">// LATEST</span></div>'
    +   '<div class="feat-body">'
    +     '<div class="fcat">' + escText(a.cat) + '</div>'
    +     '<h2><a href="' + escAttr(href) + '" rel="noopener">' + escText(a.title) + '</a></h2>'
    +     '<p>' + escText(a.excerpt) + '</p>'
    +     '<div class="fmeta"><b>' + escText(a.author) + '</b> &middot; ' + escText(a.date) + '</div>'
    +     '<a class="feat-go" href="' + escAttr(href) + '" rel="noopener">&#9656; Read Today&rsquo;s Note</a>'
    +   '</div>'
    + '</div>';
}

// --- Assemble ---
// The newest article is shown once as the featured hero, so it is excluded
// from the archive feed (no duplicate). The ticker shows the true total.
const feedItems = (articles.length ? articles.slice(1) : []).concat(authority);
const feed = feedItems.map(panelCard).join('\n');
const featured = articles.length ? featuredCard(articles[0]) : '';
const total = articles.length + authority.length;

let tpl = fs.readFileSync(TEMPLATE_FILE, 'utf8');
if (tpl.indexOf('<!--FEATURED-->') === -1 || tpl.indexOf('<!--FEED-->') === -1 || tpl.indexOf('<!--COUNT-->') === -1) {
  console.error('ERROR: template markers <!--FEATURED--> / <!--FEED--> / <!--COUNT--> not found in index-template.html');
  process.exit(1);
}
tpl = tpl.replace('<!--FEATURED-->', featured)
        .replace('<!--FEED-->', feed)
        .replace('<!--COUNT-->', total);

fs.writeFileSync(OUT_FILE, tpl, 'utf8');

console.log('✅ index.html rebuilt');
console.log('   articles:   ' + articles.length);
console.log('   authority:  ' + authority.length);
console.log('   total notes: ' + total);
console.log('   archive cards (excl. featured): ' + feedItems.length);
console.log('   featured:   ' + (articles[0] ? '#' + articles[0].n + ' ' + articles[0].title : 'none'));