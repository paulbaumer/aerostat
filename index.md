---
layout: default
---

<p>A minimalistic collection of Spotify playlists from <a href="https://aerostatbg.ru/">Aerostat Podcast</a>.</p>

<ul class="episode-list">
  {% assign sorted_episodes = site.episodes | sort: 'date' | reverse %}
  {% for episode in sorted_episodes %}
    <li class="episode-item">
      <h3><a href="{{ episode.url | relative_url }}">{{ episode.title }}</a></h3>
      <p style="font-size: 0.8em; color: #777;">Source: {{ episode.source_url }}</p>
    </li>
  {% endfor %}
</ul>
