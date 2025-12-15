(() => {
  const escapeHtml = (str) =>
    (str || "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch] || ch));

  const renderMarkdownLite = (text = "") => {
    const renderInline = (escaped) => {
      let s = escaped || "";
      s = s.replace(/`([^`]+?)`/g, "<code>$1</code>");
      s = s.replace(/\[([^\]]+?)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
      s = s.replace(/(^|[\s(])((https?:\/\/)[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
      s = s.replace(/\*\*([^*]+?)\*\*/g, "<strong>$1</strong>");
      s = s.replace(/(^|[^*])\*([^*]+?)\*(?!\*)/g, "$1<em>$2</em>");
      return s;
    };

    const lines = (text || "").replace(/\r/g, "").split("\n");
    const out = [];
    let inUl = false;
    let inOl = false;
    const closeLists = () => {
      if (inUl) out.push("</ul>");
      if (inOl) out.push("</ol>");
      inUl = false;
      inOl = false;
    };

    for (const raw of lines) {
      const line = raw || "";
      if (!line.trim()) {
        closeLists();
        continue;
      }

      const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        closeLists();
        const level = Math.min(4, Math.max(2, headingMatch[1].length + 1));
        out.push(`<h${level}>${renderInline(escapeHtml(headingMatch[2]))}</h${level}>`);
        continue;
      }

      const olMatch = line.match(/^\s*\d+\.\s+(.*)$/);
      if (olMatch) {
        if (!inOl) {
          closeLists();
          out.push('<ol class="md-list">');
          inOl = true;
        }
        out.push(`<li>${renderInline(escapeHtml(olMatch[1]))}</li>`);
        continue;
      }

      const ulMatch = line.match(/^\s*-\s+(.*)$/);
      if (ulMatch) {
        if (!inUl) {
          closeLists();
          out.push('<ul class="md-list">');
          inUl = true;
        }
        out.push(`<li>${renderInline(escapeHtml(ulMatch[1]))}</li>`);
        continue;
      }

      closeLists();
      out.push(`<p>${renderInline(escapeHtml(line))}</p>`);
    }
    closeLists();
    return out.join("");
  };

  const getCtx = () => (window.Fed101Context || {});

  const populateMeetings = async () => {
    const selects = [document.getElementById("fed101-meeting"), document.getElementById("fed101-meeting-mobile")].filter(Boolean);
    if (!selects.length) return;

    try {
      const resp = await fetch("/api/meetings");
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(data?.detail || "加载会议列表失败");

      const meetingId = (getCtx().meeting_id || "").trim();

      const historical = (data?.historical || []).slice().reverse(); // newest first
      selects.forEach((select) => {
        const frag = document.createDocumentFragment();
        for (const m of historical) {
          const opt = document.createElement("option");
          opt.value = m.meeting_id;
          opt.textContent = `${m.meeting_id} · ${m.label || ""}`;
          if (meetingId && opt.value === meetingId) opt.selected = true;
          frag.appendChild(opt);
        }
        select.appendChild(frag);
      });
    } catch (e) {
      // keep empty
    }
  };

  const restoreSidebarScroll = () => {
    const sidebar = document.querySelector(".learning-sidebar");
    if (!sidebar) return;
    try {
      const raw = sessionStorage.getItem("fed101_sidebar_scroll");
      const y = raw != null ? Number(raw) : null;
      if (y != null && Number.isFinite(y)) sidebar.scrollTop = y;
    } catch (e) {}
  };

  const wireSidebarScrollPersistence = () => {
    const sidebar = document.querySelector(".learning-sidebar");
    if (!sidebar) return;
    let raf = 0;
    const save = () => {
      raf = 0;
      try {
        sessionStorage.setItem("fed101_sidebar_scroll", String(sidebar.scrollTop || 0));
      } catch (e) {}
    };
    sidebar.addEventListener("scroll", () => {
      if (raf) return;
      raf = window.requestAnimationFrame(save);
    });
    window.addEventListener("beforeunload", save);
  };

  const applyMeetingToUrl = () => {
    const select = document.getElementById("fed101-meeting") || document.getElementById("fed101-meeting-mobile");
    if (!select) return;
    const meetingId = (select.value || "").trim();
    const url = new URL(window.location.href);
    if (meetingId) url.searchParams.set("meeting_id", meetingId);
    else url.searchParams.delete("meeting_id");
    window.location.href = url.toString();
  };

  const parseCell = (node) => {
    const raw = node.getAttribute("data-cell") || "";
    try {
      return JSON.parse(raw);
    } catch (e) {
      return { id: "cell", type: "error", params: { message: `Bad cell payload: ${e}` } };
    }
  };

  const mk = (tag, cls, text) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text != null) el.textContent = text;
    return el;
  };

  const renderNote = (host, message) => {
    host.innerHTML = `<div class="muted" style="font-size:13px; line-height:1.7;">${escapeHtml(message || "")}</div>`;
  };

  const buildOutline = () => {
    const host = document.getElementById("fed101-outline");
    const root = document.querySelector(".learning-md");
    if (!host || !root) return;
    host.innerHTML = "";

    // Only show two levels (like many doc sites): h2 (level-1) and h3 (level-2).
    // Exclude h1 because the page title is rendered separately.
    const headings = Array.from(root.querySelectorAll("h2, h3"));
    headings.forEach((h, idx) => {
      if (!h.id) h.id = `sec-${idx + 1}`;
      const level = h.tagName === "H2" ? "level-1" : "level-2";
      const a = document.createElement("a");
      a.className = `outline-item ${level}`;
      a.href = `#${h.id}`;
      a.textContent = h.textContent || "";
      host.appendChild(a);
    });

    if (!headings.length) {
      const empty = mk("div", "muted", "（本页没有标题层级）");
      empty.style.fontSize = "13px";
      host.appendChild(empty);
      return;
    }

    const itemsById = new Map();
    Array.from(host.querySelectorAll("a.outline-item")).forEach((a) => {
      const id = String(a.getAttribute("href") || "").replace(/^#/, "");
      if (id) itemsById.set(id, a);
    });

    const setActive = (id) => {
      itemsById.forEach((el, key) => {
        if (key === id) el.classList.add("active");
        else el.classList.remove("active");
      });
    };

    // Scrollspy: keep the current section highlighted.
    try {
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => (a.boundingClientRect.top || 0) - (b.boundingClientRect.top || 0));
          if (visible.length) {
            const id = visible[0]?.target?.id;
            if (id) setActive(id);
          }
        },
        { root: null, rootMargin: "-20% 0px -70% 0px", threshold: [0, 1] }
      );
      headings.forEach((h) => observer.observe(h));
      // Default to first item.
      setActive(headings[0]?.id);
    } catch (e) {
      // ignore
    }
  };

  const renderIndicatorSeries = (host, result) => {
    const series = result?.series || [];
    if (!series.length) {
      renderNote(host, "无数据（可能还未同步指标数据库）。");
      return;
    }

    host.innerHTML = "";
    for (const s of series) {
      const wrap = mk("div", "f101-output-card");
      const head = mk("div", "f101-output-head");
      head.innerHTML = `<div class="f101-output-title">${escapeHtml(s.name || s.code || "")}</div><div class="muted" style="font-size:12px;">${escapeHtml(s.code || "")} · ${escapeHtml(s.units || "")}</div>`;
      wrap.appendChild(head);

      const canvas = document.createElement("canvas");
      canvas.height = 140;
      const canvasWrap = mk("div", "chart-box");
      canvasWrap.appendChild(canvas);
      wrap.appendChild(canvasWrap);
      host.appendChild(wrap);

      const labels = (s.dates || []).map((d) => String(d).slice(0, 10));
      const values = (s.values || []).map((v) => (v == null ? null : Number(v)));

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: s.code || "series",
              data: values,
              borderColor: "#38bdf8",
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              borderWidth: 2,
              pointRadius: 0,
              tension: 0.2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 6 }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 5 }, grid: { color: "rgba(255,255,255,0.06)" } },
          },
        },
      });
    }
  };

  const renderTaylor = (host, result) => {
    const metrics = result?.metrics || {};
    const series = result?.series || [];
    const explain = result?.explain || {};

    const top = mk("div", "f101-output-metrics");
    top.innerHTML = `
      <div class="metric"><div class="muted">Taylor</div><div class="title">${metrics.taylorLatest != null ? Number(metrics.taylorLatest).toFixed(2) + "%" : "—"}</div></div>
      <div class="metric"><div class="muted">EFFR</div><div class="title">${metrics.fedLatest != null ? Number(metrics.fedLatest).toFixed(2) + "%" : "—"}</div></div>
      <div class="metric"><div class="muted">利差</div><div class="title">${metrics.spread != null ? Number(metrics.spread).toFixed(2) + "%" : "—"}</div></div>
    `;
    host.innerHTML = "";
    host.appendChild(top);

    if (!series.length) {
      renderNote(host, "无模型序列输出（可能还未同步关键指标）。");
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.height = 180;
    const chartWrap = mk("div", "chart-box");
    chartWrap.appendChild(canvas);
    host.appendChild(chartWrap);

    const labels = series.map((p) => String(p.date || "").slice(0, 10));
    const fed = series.map((p) => (p.fed != null ? Number(p.fed) : null));
    const taylor = series.map((p) => (p.taylor != null ? Number(p.taylor) : null));
    const adjusted = series.map((p) => (p.adjusted != null ? Number(p.adjusted) : null));

    // eslint-disable-next-line no-undef
    new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "EFFR", data: fed, borderColor: "#22c55e", pointRadius: 0, borderWidth: 2, tension: 0.2 },
          { label: "Taylor", data: taylor, borderColor: "#38bdf8", pointRadius: 0, borderWidth: 2, tension: 0.2 },
          { label: "Adj", data: adjusted, borderColor: "#f59e0b", pointRadius: 0, borderWidth: 2, tension: 0.2 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { labels: { color: "rgba(233,237,245,0.75)" } } },
        scales: {
          x: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 6 }, grid: { color: "rgba(255,255,255,0.06)" } },
          y: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 5 }, grid: { color: "rgba(255,255,255,0.06)" } },
        },
      },
    });

    const explainBlock = mk("div", "muted");
    explainBlock.style.fontSize = "13px";
    explainBlock.style.lineHeight = "1.7";
    explainBlock.style.marginTop = "10px";
    explainBlock.innerHTML = renderMarkdownLite(
      [
        `- As of: \`${explain.as_of || "—"}\``,
        `- Model: \`${explain.model || "—"}\``,
        `- Inflation transform: \`${explain.inflation_transform || "raw"}\``,
      ].join("\n")
    );
    host.appendChild(explainBlock);
  };

  const renderStatementDiff = (host, result) => {
    const meetingId = result?.meeting_id;
    const prevId = result?.previous_meeting_id;
    const cur = result?.current || {};
    const prev = result?.previous || {};
    const diff = result?.diff || {};
    const cta = result?.cta || {};

    const header = mk("div", "muted");
    header.style.fontSize = "13px";
    header.style.lineHeight = "1.7";
    header.innerHTML = renderMarkdownLite(
      [
        `- 当前会议：\`${meetingId || "—"}\``,
        `- 上一次会议：\`${prevId || "—"}\``,
        cta?.hint ? `- 提示：${cta.hint}` : "",
      ].filter(Boolean).join("\n")
    );

    const link = cta?.generate_url ? `<a class="chip" href="${escapeHtml(cta.generate_url)}" target="_blank" rel="noopener noreferrer">打开决议/纪要页</a>` : "";
    const chips = mk("div", "chips");
    chips.innerHTML = link;

    const block = mk("div", "f101-diff-grid");
    const mkPane = (title, a, b, d) => {
      const pane = mk("div", "card f101-diff-pane");
      pane.innerHTML = `
        <div class="title">${escapeHtml(title)}</div>
        <div class="muted" style="font-size:12px;">缺失时请先生成并缓存。</div>
        <div class="f101-diff-inner">
          <div>
            <div class="chip">上一期</div>
            <pre class="codeblock">${escapeHtml((a || "").slice(0, 4000) || "（空）")}</pre>
          </div>
          <div>
            <div class="chip">本期</div>
            <pre class="codeblock">${escapeHtml((b || "").slice(0, 4000) || "（空）")}</pre>
          </div>
        </div>
        <div style="margin-top:10px;">
          <div class="chip">Diff（unified）</div>
          <pre class="codeblock">${escapeHtml((d || "").slice(0, 8000) || "（无 diff）")}</pre>
        </div>
      `;
      return pane;
    };

    block.appendChild(mkPane("Statement（生成稿）", prev.statement, cur.statement, diff.statement));
    block.appendChild(mkPane("Minutes Summary（生成稿）", prev.minutes_summary, cur.minutes_summary, diff.minutes_summary));

    host.innerHTML = "";
    host.appendChild(header);
    host.appendChild(chips);
    host.appendChild(block);
  };

  const renderDecisionBrief = (host, result) => {
    const ok = !!result?.available;
    const meetingId = result?.meeting_id;
    const cta = result?.cta || {};
    host.innerHTML = "";

    if (!ok) {
      const msg = mk("div", "muted");
      msg.style.fontSize = "13px";
      msg.style.lineHeight = "1.7";
      msg.innerHTML = renderMarkdownLite(
        [
          `- meeting_id: \`${meetingId || "—"}\``,
          result?.message ? `- ${result.message}` : "",
        ].filter(Boolean).join("\n")
      );
      host.appendChild(msg);
      if (cta?.generate_url) {
        const chips = mk("div", "chips");
        chips.innerHTML = `<a class="chip" href="${escapeHtml(cta.generate_url)}" target="_blank" rel="noopener noreferrer">打开决议/纪要页生成</a>`;
        host.appendChild(chips);
      }
      return;
    }

    const analysis = result?.analysis || {};
    const top = mk("div", "chips");
    top.innerHTML = `
      <span class="chip">meeting_id: ${escapeHtml(meetingId || "—")}</span>
      ${cta?.generate_url ? `<a class="chip" href="${escapeHtml(cta.generate_url)}" target="_blank" rel="noopener noreferrer">打开决议/纪要页</a>` : ""}
    `;
    host.appendChild(top);

    const bullets = [];
    const stmtHeads = analysis?.statement_headings || [];
    const minHeads = analysis?.minutes_headings || [];
    if (stmtHeads.length) bullets.push(`- Statement 结构：${stmtHeads.slice(0, 6).map((x) => `\`${x}\``).join(" · ")}`);
    if (minHeads.length) bullets.push(`- Minutes 结构：${minHeads.slice(0, 6).map((x) => `\`${x}\``).join(" · ")}`);
    const terms = (analysis?.top_terms || []).slice(0, 10).map((t) => `\`${t.term}\`(${t.count})`).join(" · ");
    if (terms) bullets.push(`- 高频词（仅供定位主题）：${terms}`);
    const tips = [
      "- 先看：政策动作（加/降/按兵不动）与对通胀/就业的定性判断是否更强或更弱。",
      "- 再看：风险表述（upside/downside、uncertainty）与前瞻指引（保持限制性/逐步调整）。",
      "- 最后看：Minutes 里“分歧与权衡”是否集中在通胀粘性、增长放缓或金融条件。",
    ];

    const note = mk("div", "muted");
    note.style.fontSize = "13px";
    note.style.lineHeight = "1.7";
    note.innerHTML = renderMarkdownLite(bullets.concat(tips).join("\n"));
    host.appendChild(note);

    const panes = mk("div", "f101-diff-inner");
    const mkDoc = (title, md) => {
      const pane = mk("div", "");
      pane.innerHTML = `<div class="chip">${escapeHtml(title)}</div><pre class="codeblock">${escapeHtml((md || "").slice(0, 12000) || "（空）")}</pre>`;
      return pane;
    };
    panes.appendChild(mkDoc("Statement（生成稿）", result?.statement_md));
    panes.appendChild(mkDoc("Minutes Summary（生成稿）", result?.minutes_md));
    host.appendChild(panes);
  };

  const filterWindow = (series, years) => {
    const arr = Array.isArray(series) ? series : [];
    if (!arr.length) return arr;
    const end = new Date(String(arr[arr.length - 1]?.date || "").slice(0, 10));
    if (!Number.isFinite(end.getTime())) return arr;
    const start = new Date(end);
    start.setFullYear(start.getFullYear() - years);
    return arr.filter((p) => {
      const d = new Date(String(p?.date || "").slice(0, 10));
      return Number.isFinite(d.getTime()) && d >= start;
    });
  };

  const renderLaborFigure = (host, result) => {
    const fig = result?.figure;
    const month = result?.month;
    const data = result?.data || {};
    host.innerHTML = "";

    const header = mk("div", "muted");
    header.style.fontSize = "13px";
    header.style.lineHeight = "1.7";
    header.innerHTML = renderMarkdownLite(
      [
        `- month: \`${month || "—"}\``,
        result?.headline_summary ? `- headline: ${result.headline_summary}` : "",
      ].filter(Boolean).join("\n")
    );
    host.appendChild(header);

    if (fig === "fig1" || fig === "chart1") {
      const payems = Array.isArray(data.payems_series) ? data.payems_series : [];
      const unrate = Array.isArray(data.unemployment_series) ? data.unemployment_series : [];
      if (!payems.length) {
        renderNote(host, "无新增非农序列数据（可能该月份数据缺失）。");
        return;
      }

      const labels = payems.map((p) => String(p.date || "").slice(0, 10)).filter(Boolean);
      const unempMap = new Map(unrate.map((u) => [String(u.date || "").slice(0, 10), u.value]));
      const payemsVals = payems.map((p) => (p.monthly_change_10k ?? p.value ?? null));
      const unrateVals = labels.map((d) => (unempMap.get(d) ?? null));

      const canvas = document.createElement("canvas");
      canvas.height = 220;
      const chartWrap = mk("div", "chart-box");
      chartWrap.appendChild(canvas);
      host.appendChild(chartWrap);

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              type: "bar",
              label: "新增非农（万人）",
              data: payemsVals,
              yAxisID: "y",
              backgroundColor: "rgba(56, 189, 248, 0.25)",
              borderColor: "rgba(56, 189, 248, 0.95)",
              borderWidth: 1,
              order: 2,
            },
            {
              type: "line",
              label: "失业率（%）",
              data: unrateVals,
              yAxisID: "y1",
              borderColor: "#f59e0b",
              borderWidth: 2,
              pointRadius: 3,
              pointHitRadius: 10,
              pointHoverRadius: 3,
              tension: 0.2,
              order: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { labels: { color: "rgba(233,237,245,0.75)" } },
            tooltip: { mode: "index", intersect: false, backgroundColor: "rgba(8,16,28,0.9)", titleColor: "#fff", bodyColor: "#fff" },
          },
          scales: {
            x: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 7 }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 5 }, grid: { color: "rgba(255,255,255,0.06)" }, title: { display: true, text: "万人", color: "rgba(233,237,245,0.6)" } },
            y1: { position: "right", ticks: { color: "rgba(233,237,245,0.75)", maxTicksLimit: 5 }, grid: { drawOnChartArea: false }, title: { display: true, text: "%", color: "rgba(233,237,245,0.6)" } },
          },
        },
      });
      return;
    }

    if (fig === "unemployment_types" || fig === "chart3") {
      const rows = Array.isArray(data.unemployment_types_series) ? data.unemployment_types_series : [];
      if (!rows.length) {
        renderNote(host, "无失业率口径数据。");
        return;
      }

      const labels = rows.map((s) => s.label);
      const prevVals = rows.map((s) => (s.previous ?? null));
      const currVals = rows.map((s) => (s.current ?? null));

      const canvas = document.createElement("canvas");
      canvas.height = 240;
      const chartWrap = mk("div", "chart-box");
      chartWrap.appendChild(canvas);
      host.appendChild(chartWrap);

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "bar",
        data: {
          labels,
          datasets: [
            { label: "上月", data: prevVals, backgroundColor: "rgba(148, 163, 184, 0.55)", borderColor: "rgba(148, 163, 184, 0.9)", categoryPercentage: 0.6, barPercentage: 0.9, maxBarThickness: 34, borderRadius: 6 },
            { label: "本月", data: currVals, backgroundColor: "rgba(56, 189, 248, 0.75)", borderColor: "rgba(56, 189, 248, 0.95)", categoryPercentage: 0.6, barPercentage: 0.9, maxBarThickness: 34, borderRadius: 6 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { labels: { color: "rgba(233,237,245,0.75)" } },
            tooltip: { mode: "index", intersect: false, backgroundColor: "rgba(8,16,28,0.9)", titleColor: "#fff", bodyColor: "#fff" },
          },
          scales: {
            x: { ticks: { color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" }, title: { display: true, text: "%", color: "rgba(233,237,245,0.6)" } },
          },
        },
      });
      return;
    }

    if (fig === "employment_participation" || fig === "chart4") {
      const series = Array.isArray(data.employment_participation_series) ? data.employment_participation_series : [];
      if (!series.length) {
        renderNote(host, "无就业率/参与率序列。");
        return;
      }
      const labels = series.map((s) => String(s.date || "").slice(0, 10)).filter(Boolean);
      const emp = series.map((s) => (s.employment_rate ?? null));
      const part = series.map((s) => (s.participation_rate ?? null));

      const canvas = document.createElement("canvas");
      canvas.height = 220;
      const chartWrap = mk("div", "chart-box");
      chartWrap.appendChild(canvas);
      host.appendChild(chartWrap);

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            { label: "就业率(%)", data: emp, borderColor: "rgba(56, 189, 248, 0.95)", backgroundColor: "rgba(56,189,248,0.10)", tension: 0.22, pointRadius: 0 },
            { label: "劳动参与率(%)", data: part, borderColor: "rgba(167, 139, 250, 0.95)", backgroundColor: "rgba(167,139,250,0.10)", tension: 0.22, pointRadius: 0 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { labels: { color: "rgba(233,237,245,0.75)" } },
            tooltip: { mode: "index", intersect: false, backgroundColor: "rgba(8,16,28,0.9)", titleColor: "#fff", bodyColor: "#fff" },
          },
          scales: {
            x: { ticks: { maxTicksLimit: 8, color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" }, title: { display: true, text: "%", color: "rgba(233,237,245,0.6)" } },
          },
        },
      });
      return;
    }

    if (fig === "industry_contribution" || fig === "chart2") {
      const contrib = data.industry_contribution || {};
      const labels = contrib.labels || [];
      const datasets = contrib.datasets || [];
      if (!labels.length || !datasets.length || contrib.error) {
        renderNote(host, contrib.error || "无分行业贡献数据。");
        return;
      }

      const canvas = document.createElement("canvas");
      canvas.height = 340;
      const chartWrap = mk("div", "chart-box");
      chartWrap.appendChild(canvas);
      host.appendChild(chartWrap);

      const yLabels = labels.slice().reverse();
      const chartDataSets = datasets.map((ds, idx) => {
        const base = idx % 8;
        const palette = [
          "rgba(56, 189, 248, 0.75)",
          "rgba(34, 211, 238, 0.65)",
          "rgba(34, 197, 94, 0.65)",
          "rgba(245, 158, 11, 0.62)",
          "rgba(168, 85, 247, 0.55)",
          "rgba(244, 63, 94, 0.50)",
          "rgba(148, 163, 184, 0.55)",
          "rgba(99, 102, 241, 0.55)",
        ];
        return {
          label: ds.label || ds.code || `ds${idx + 1}`,
          data: (ds.data || []).slice().reverse(),
          backgroundColor: palette[base],
          borderWidth: 0,
          stack: "stack1",
        };
      });

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "bar",
        data: { labels: yLabels, datasets: chartDataSets },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { display: false },
            tooltip: { mode: "index", intersect: false, backgroundColor: "rgba(8,16,28,0.9)", titleColor: "#fff", bodyColor: "#fff" },
          },
          scales: {
            x: {
              stacked: true,
              ticks: { color: "rgba(233,237,245,0.75)" },
              grid: { color: "rgba(255,255,255,0.06)" },
              title: { display: true, text: "贡献率(%)", color: "rgba(233,237,245,0.6)" },
            },
            y: { stacked: true, ticks: { color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.04)" } },
          },
        },
      });
      return;
    }

    renderNote(host, `未知 labor figure: ${fig}`);
  };

  const renderContribTableSimple = (rows, title) => {
    const wrap = mk("div", "f101-output-card");
    wrap.innerHTML = `<div class="f101-output-title">${escapeHtml(title || "Contributions")}</div><div class="muted" style="font-size:12px;">按 |拉动| 排序，展示前 12 项（含正负）</div>`;
    const arr = Array.isArray(rows) ? rows.slice() : [];
    arr.sort((a, b) => Math.abs(Number(b?.contribution || 0)) - Math.abs(Number(a?.contribution || 0)));
    const top = arr.slice(0, 12);
    const lines = top.map((r) => {
      const label = r.label || r.code || "";
      const w = r.weight != null ? `w=${Number(r.weight).toFixed(2)}%` : "w=—";
      const cur = r.current != null ? `cur=${Number(r.current).toFixed(2)}` : "cur=—";
      const prev = r.previous != null ? `prev=${Number(r.previous).toFixed(2)}` : "prev=—";
      const c = r.contribution != null ? `contrib=${Number(r.contribution).toFixed(2)}` : "contrib=—";
      const d = r.delta_contribution != null ? `Δ=${Number(r.delta_contribution).toFixed(2)}` : "Δ=—";
      return `${label}\t${w}\t${cur}\t${prev}\t${c}\t${d}`;
    });
    const pre = mk("pre", "codeblock");
    pre.textContent = lines.join("\n");
    wrap.appendChild(pre);
    return wrap;
  };

  const renderCpiFigure = (host, result) => {
    const fig = result?.figure;
    const month = result?.month;
    const data = result?.data || {};
    host.innerHTML = "";

    const header = mk("div", "muted");
    header.style.fontSize = "13px";
    header.style.lineHeight = "1.7";
    header.innerHTML = renderMarkdownLite(
      [
        `- month: \`${month || "—"}\``,
        result?.headline_summary ? `- headline: ${result.headline_summary}` : "",
        result?.weight_year ? `- 权重年份：\`${result.weight_year}\`` : "",
      ].filter(Boolean).join("\n")
    );
    host.appendChild(header);

    if (fig === "yoy" || fig === "mom" || fig === "chart1" || fig === "chart2") {
      const normalized = fig === "chart1" ? "yoy" : fig === "chart2" ? "mom" : fig;
      const isYoy = normalized === "yoy";
      const series = isYoy ? (data.yoy_series || []) : (data.mom_series || []);
      if (!series.length) {
        renderNote(host, "无序列数据。");
        return;
      }
      const labels = series.map((p) => String(p.date).slice(0, 10));
      const cpi = series.map((p) => (isYoy ? (p.cpi_yoy ?? null) : (p.cpi_mom ?? null)));
      const core = series.map((p) => (isYoy ? (p.core_yoy ?? null) : (p.core_mom ?? null)));

      const canvas = document.createElement("canvas");
      canvas.height = 220;
      const chartWrap = mk("div", "chart-box");
      chartWrap.appendChild(canvas);
      host.appendChild(chartWrap);

      // eslint-disable-next-line no-undef
      new Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            { label: isYoy ? "CPI" : "CPI", data: cpi, borderColor: "rgba(56, 189, 248, 0.95)", backgroundColor: "rgba(56,189,248,0.10)", tension: 0.22, pointRadius: 0 },
            { label: isYoy ? "核心CPI" : "核心CPI", data: core, borderColor: "rgba(167, 139, 250, 0.95)", backgroundColor: "rgba(167,139,250,0.10)", tension: 0.22, pointRadius: 0 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: { legend: { labels: { color: "rgba(233,237,245,0.75)" } }, tooltip: { mode: "index", intersect: false, backgroundColor: "rgba(8,16,28,0.9)", titleColor: "#fff", bodyColor: "#fff" } },
          scales: {
            x: { ticks: { maxTicksLimit: 8, color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "rgba(233,237,245,0.75)" }, grid: { color: "rgba(255,255,255,0.06)" }, title: { display: true, text: isYoy ? "同比(%)" : "环比(%)", color: "rgba(233,237,245,0.6)" } },
          },
        },
      });
      return;
    }

    if (fig === "contrib_yoy") {
      const renderFn = window?.FomcReportRender?.renderContribTable;
      if (typeof renderFn === "function") host.appendChild(renderFn("表：同比拉动拆分", data.contributions_yoy || [], "yoy"));
      else host.appendChild(renderContribTableSimple(data.contributions_yoy || [], "同比拉动拆分（Top）"));
      return;
    }
    if (fig === "contrib_mom") {
      const renderFn = window?.FomcReportRender?.renderContribTable;
      if (typeof renderFn === "function") host.appendChild(renderFn("表：环比拉动拆分", data.contributions_mom || [], "mom"));
      else host.appendChild(renderContribTableSimple(data.contributions_mom || [], "环比拉动拆分（Top）"));
      return;
    }

    renderNote(host, `未知 cpi figure: ${fig}`);
  };

  const resolveMeetingMonth = async (meetingId) => {
    const mid = (meetingId || "").trim();
    if (!mid) return null;
    try {
      const resp = await fetch(`/api/history/${encodeURIComponent(mid)}/context`);
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) return null;
      const months = data?.report_months || [];
      const focus = months.length ? months[months.length - 1] : null;
      return focus || null; // YYYY-MM
    } catch (e) {
      return null;
    }
  };

  const renderToolboxEmbed = async (host, cell) => {
    const params = cell?.params || {};
    const tab = params.tab || "pane-labor";
    const height = Number(params.height || 760);
    const wantMonth = params.month || null;
    const useMeetingMonth = !!params.use_meeting_month;

    let month = wantMonth;
    if (!month && useMeetingMonth) {
      month = await resolveMeetingMonth(getCtx().meeting_id);
    }

    const url = new URL(window.location.origin + "/toolbox");
    url.searchParams.set("embed", "1");
    url.searchParams.set("tab", tab);
    if (month) url.searchParams.set("month", month);

    host.innerHTML = "";
    const frameWrap = mk("div", "f101-iframe");
    const iframe = document.createElement("iframe");
    iframe.src = url.toString();
    iframe.loading = "lazy";
    iframe.style.height = `${Number.isFinite(height) ? height : 760}px`;
    frameWrap.appendChild(iframe);
    host.appendChild(frameWrap);
  };

  const buildControls = (cell, onChange) => {
    const schema = cell?.controls || [];
    if (!Array.isArray(schema) || !schema.length) return null;
    const box = mk("div", "f101-controls");

    schema.forEach((c) => {
      const key = c?.key;
      if (!key) return;
      const kind = c?.type || "text";
      const wrap = mk("div", "f101-control");
      const label = mk("label", "", c?.label || key);
      wrap.appendChild(label);

      let input = null;
      if (kind === "select") {
        input = document.createElement("select");
        (c?.options || []).forEach((opt) => {
          const o = document.createElement("option");
          if (typeof opt === "string") {
            o.value = opt;
            o.textContent = opt;
          } else {
            o.value = opt?.value;
            o.textContent = opt?.label || opt?.value;
          }
          input.appendChild(o);
        });
      } else if (kind === "number") {
        input = document.createElement("input");
        input.type = "number";
        if (c?.step != null) input.step = String(c.step);
        if (c?.min != null) input.min = String(c.min);
        if (c?.max != null) input.max = String(c.max);
      } else {
        input = document.createElement("input");
        input.type = "text";
      }

      input.value = cell?.params?.[key] != null ? String(cell.params[key]) : c?.default != null ? String(c.default) : "";
      input.addEventListener("change", () => {
        let val = input.value;
        if (kind === "number") val = Number(val);
        cell.params = cell.params || {};
        cell.params[key] = val;
        onChange && onChange(cell);
      });

      wrap.appendChild(input);
      box.appendChild(wrap);
    });

    return box;
  };

  const runCell = async (cell, outputEl, statusEl) => {
    statusEl.innerHTML = `<span class="f101-spinner"></span> 运行中…`;
    try {
      const payload = { type: cell.type, params: cell.params || {}, context: { meeting_id: getCtx().meeting_id || "" } };
      const resp = await fetch("/api/fed101/cell", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(data?.detail || "运行失败");

      const kind = data?.kind || "note";
      if (kind === "indicator_series") renderIndicatorSeries(outputEl, data);
      else if (kind === "meeting_statement_diff") renderStatementDiff(outputEl, data);
      else if (kind === "meeting_decision_brief") renderDecisionBrief(outputEl, data);
      else if (kind === "labor_figure") renderLaborFigure(outputEl, data);
      else if (kind === "cpi_figure") renderCpiFigure(outputEl, data);
      else if (cell.type === "taylor_model") renderTaylor(outputEl, data);
      else renderNote(outputEl, data?.message || "完成");

      statusEl.textContent = "完成";
    } catch (e) {
      statusEl.textContent = `错误：${e.message || e}`;
      outputEl.innerHTML = `<div class="muted" style="color: var(--danger);">${escapeHtml(String(e.message || e))}</div>`;
    }
  };

  const hydrateCells = () => {
    const nodes = Array.from(document.querySelectorAll(".f101-cell"));
    nodes.forEach((node) => {
      const cell = parseCell(node);
      const wrapper = mk("div", "card f101-cell-card");
      const head = mk("div", "f101-cell-head");
      const title = cell?.title || cell?.type || "cell";
      head.innerHTML = `
        <div>
          <div class="f101-cell-title">${escapeHtml(title)}</div>
          <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
            <span class="f101-badge">type: ${escapeHtml(cell?.type || "")}</span>
            ${cell?.id ? `<span class="f101-badge">id: ${escapeHtml(cell.id)}</span>` : ""}
          </div>
          ${cell?.note ? `<div class="muted" style="font-size:13px; margin-top:10px;">${escapeHtml(cell.note)}</div>` : ""}
        </div>
      `;

      const controls = mk("div", "f101-cell-controls");
      const dynamicControls = buildControls(cell, () => {});
      const btn = mk("button", "btn secondary", "运行");
      btn.type = "button";
      const status = mk("span", "muted", "");
      status.style.fontSize = "13px";
      if (dynamicControls) controls.appendChild(dynamicControls);
      controls.appendChild(btn);
      controls.appendChild(status);

      const output = mk("div", "f101-cell-output");
      renderNote(output, "点击“运行”执行该小组件。");

      wrapper.appendChild(head);
      wrapper.appendChild(controls);
      wrapper.appendChild(output);

      btn.addEventListener("click", async () => {
        if (cell?.type === "toolbox_embed") {
          status.innerHTML = `<span class="f101-spinner"></span> 加载中…`;
          await renderToolboxEmbed(output, cell);
          status.textContent = "完成";
          return;
        }
        await runCell(cell, output, status);
      });

      node.replaceWith(wrapper);

      if (cell?.autorun) {
        if (cell?.type === "toolbox_embed") {
          renderToolboxEmbed(output, cell).catch(() => {});
          status.textContent = "";
        } else {
          runCell(cell, output, status);
        }
      }
    });

    buildOutline();
  };

  document.getElementById("fed101-apply")?.addEventListener("click", applyMeetingToUrl);
  document.getElementById("fed101-apply-mobile")?.addEventListener("click", applyMeetingToUrl);

  const openToc = () => {
    const overlay = document.getElementById("fed101-toc-overlay");
    if (!overlay) return;
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    document.getElementById("fed101-toc-filter")?.focus();
  };

  const closeToc = () => {
    const overlay = document.getElementById("fed101-toc-overlay");
    if (!overlay) return;
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
  };

  document.getElementById("fed101-toc-open")?.addEventListener("click", openToc);
  document.getElementById("fed101-toc-close")?.addEventListener("click", closeToc);
  document.getElementById("fed101-toc-overlay")?.addEventListener("click", (e) => {
    if (e.target?.id === "fed101-toc-overlay") closeToc();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeToc();
  });

  const filterToc = () => {
    const input = document.getElementById("fed101-toc-filter");
    const q = (input?.value || "").trim().toLowerCase();
    const list = document.getElementById("fed101-toc-list");
    if (!list) return;
    Array.from(list.querySelectorAll("a.toc-item")).forEach((a) => {
      const t = (a.getAttribute("data-title") || "").toLowerCase();
      const s = (a.getAttribute("data-slug") || "").toLowerCase();
      const ok = !q || t.includes(q) || s.includes(q);
      a.style.display = ok ? "" : "none";
    });
  };
  document.getElementById("fed101-toc-filter")?.addEventListener("input", filterToc);

  restoreSidebarScroll();
  wireSidebarScrollPersistence();

  populateMeetings().then(hydrateCells).catch(hydrateCells);
})();
