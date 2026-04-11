window.addEventListener("DOMContentLoaded", () => {
  const updateStargazerCount = () => {
    const target = document.querySelector("#stargazers");
    if (!target) {
      return;
    }

    const shieldsUrl =
      "https://img.shields.io/github/stars/keenlycode/dictify?style=flat&label=&color=111827&logo=github&logoColor=white";

    fetch(shieldsUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Unable to load star count: ${response.status}`);
        }
        return response.text();
      })
      .then((svg) => {
        const doc = new DOMParser().parseFromString(svg, "image/svg+xml");
        const values = [...doc.querySelectorAll("text")]
          .map((node) => node.textContent.trim())
          .filter((text) => /^\d[\d.]*[kM]?$/.test(text));

        const count = values.at(-1);
        if (count) {
          target.textContent = count;
        }
      })
      .catch(() => {
        target.textContent = "";
      });
  };

  updateStargazerCount();

  const ensureTrailingSlash = (value) => value.replace(/\/?$/, "/");
  const versionRoot = new URL(ensureTrailingSlash(base_url), window.location.origin);
  const versionPath = versionRoot.pathname;
  const currentPath = window.location.pathname;
  const relativePath = currentPath.startsWith(versionPath)
    ? currentPath.slice(versionPath.length)
    : "";
  const currentIdentifier = versionPath.split("/").filter(Boolean).at(-1);
  const versionsUrl = new URL("../versions.json", versionRoot);
  const latestHomeUrl = new URL("/dictify/latest/", window.location.origin);

  const buildVersionUrl = (identifier) => new URL(`../${identifier}/${relativePath}`, versionRoot);

  const createSelector = (versions, currentVersion) => {
    const container = document.querySelector("#version-selector");
    if (!container) {
      return;
    }

    const select = document.createElement("select");
    select.className = "version-select";
    select.setAttribute("aria-label", "Select documentation version");

    versions
      .filter((entry) => !(entry.properties && entry.properties.hidden) || entry.version === currentVersion)
      .forEach((entry) => {
        const option = new Option(entry.title, entry.version, false, entry.version === currentVersion);
        select.add(option);
      });

    select.addEventListener("change", () => {
      window.location.href = buildVersionUrl(select.value).toString();
    });

    container.replaceChildren(select);
    container.classList.remove("hidden");
  };

  const createOutdatedBanner = (latestVersion) => {
    if (!latestVersion) {
      return;
    }

    const pageHeader = document.querySelector("#page-header");
    if (!pageHeader) {
      return;
    }

    const banner = document.createElement("div");
    banner.className = "version-banner";

    const text = document.createElement("span");
    text.textContent = "You are viewing an older version of the docs.";

    const link = document.createElement("a");
    link.href = buildVersionUrl("latest").toString();
    link.textContent = `Open ${latestVersion.title}.`;

    banner.append(text, link);
    pageHeader.parentNode.insertBefore(banner, pageHeader);
  };

  fetch(versionsUrl)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Unable to load versions: ${response.status}`);
      }
      return response.json();
    })
    .then((versions) => {
      if (!Array.isArray(versions) || versions.length === 0) {
        return;
      }

      const currentVersion = versions.find(
        (entry) => entry.version === currentIdentifier || entry.aliases.includes(currentIdentifier),
      );
      const latestVersion = versions.find((entry) => entry.aliases.includes("latest"));

      if (!currentVersion) {
        return;
      }

      createSelector(versions, currentVersion.version);

      if (latestVersion && latestVersion.version !== currentVersion.version) {
        createOutdatedBanner(latestVersion);
      }
    })
    .catch(() => {
      const logoLink = document.querySelector('header a[href$="/latest/"]');
      if (logoLink) {
        logoLink.href = latestHomeUrl.toString();
      }
    });
});
