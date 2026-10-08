<script>
	import { onMount } from 'svelte';
	import { env } from '$env/dynamic/public';

	const API_BASE = (env.PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

	let inputUrl = '';
	let isLoading = false;
	let errorMessage = '';
	let videoData = null;
	let activeTab = 'video';
	let downloadingKey = null;
	let downloadSuccessMessage = '';

	const youtubeRegex = /^(https?:\/\/)?(www\.|m\.|music\.)?(youtube\.com\/(watch\?.*v=|shorts\/|embed\/|v\/)|youtu\.be\/)[a-zA-Z0-9_-]{11}/;

	async function handlePaste() {
		try {
			if (navigator.clipboard && navigator.clipboard.readText) {
				const text = await navigator.clipboard.readText();
				if (text) {
					inputUrl = text.trim();
					errorMessage = '';
				}
			}
		} catch (err) {
			errorMessage = 'Izin clipboard tidak diberikan. Silakan tempel tautan secara manual.';
		}
	}

	function handleClear() {
		inputUrl = '';
		errorMessage = '';
		videoData = null;
		downloadingKey = null;
		downloadSuccessMessage = '';
	}

	async function fetchVideoInfo() {
		const trimmedUrl = inputUrl.trim();
		if (!trimmedUrl) {
			errorMessage = 'Silakan masukkan tautan video YouTube.';
			return;
		}

		if (!youtubeRegex.test(trimmedUrl)) {
			errorMessage = 'Format tautan tidak valid. Pastikan URL berasal dari youtube.com atau youtu.be.';
			return;
		}

		isLoading = true;
		errorMessage = '';
		videoData = null;
		downloadSuccessMessage = '';

		try {
			const res = await fetch(`${API_BASE}/api/info`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ url: trimmedUrl })
			});

			const data = await res.json();

			if (!res.ok) {
				throw new Error(data.detail || 'Gagal memproses informasi video dari server.');
			}

			videoData = data;
		} catch (err) {
			errorMessage = err.message || 'Tidak dapat terhubung ke server backend Tubi.';
		} finally {
			isLoading = false;
		}
	}

	function triggerDownload(type, quality) {
		if (!videoData) return;

		const key = `${type}-${quality}`;
		downloadingKey = key;
		downloadSuccessMessage = '';

		const params = new URLSearchParams({
			url: videoData.url,
			type: type,
			quality: quality,
			title: videoData.title
		});

		const downloadUrl = `${API_BASE}/api/download?${params.toString()}`;

		// Trigger download via invisible anchor tag
		const a = document.createElement('a');
		a.href = downloadUrl;
		a.setAttribute('download', '');
		a.style.display = 'none';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		setTimeout(() => {
			downloadingKey = null;
			downloadSuccessMessage = `Permintaan unduhan ${type.toUpperCase()} (${quality}) telah dikirim ke browser.`;
		}, 2000);
	}

	function formatViews(count) {
		if (!count && count !== 0) return 'Tidak diketahui';
		if (count >= 1000000) {
			return `${(count / 1000000).toFixed(1)} jt tayangan`;
		}
		if (count >= 1000) {
			return `${(count / 1000).toFixed(1)} rb tayangan`;
		}
		return `${count} tayangan`;
	}
</script>

<svelte:head>
	<title>Tubi: YouTube Video dan Audio Downloader</title>
</svelte:head>

<!-- Header -->
<header class="border-b border-tubi-border bg-tubi-card/60 backdrop-blur-md sticky top-0 z-20">
	<div class="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-lg bg-tubi-accent flex items-center justify-center text-white font-bold text-lg shadow-sm">
				T
			</div>
			<div>
				<span class="font-bold text-lg tracking-tight text-white">Tubi</span>
				<span class="text-xs text-tubi-muted ml-2 font-mono px-2 py-0.5 rounded bg-tubi-elevated border border-tubi-border">v1.0</span>
			</div>
		</div>

		<div class="flex items-center gap-2 text-xs text-tubi-muted">
			<span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
			<span>Layanan Aktif</span>
		</div>
	</div>
</header>

<!-- Main Container -->
<main class="flex-1 max-w-4xl w-full mx-auto px-4 py-8 md:py-12 flex flex-col gap-8">
	<!-- Hero Header -->
	<div class="text-center space-y-3">
		<h1 class="text-2xl md:text-4xl font-bold tracking-tight text-white">
			Pengunduh Media YouTube Cepat dan Bersih
		</h1>
		<p class="text-sm md:text-base text-tubi-muted max-w-xl mx-auto leading-relaxed">
			Unduh video format MP4 resolusi hingga 1080p atau audio MP3 jernih langsung ke perangkat Anda tanpa iklan yang mengganggu.
		</p>
	</div>

	<!-- Input Section -->
	<section aria-label="Input URL Video" class="bg-tubi-card border border-tubi-border rounded-xl p-4 md:p-6 shadow-sm">
		<form on:submit|preventDefault={fetchVideoInfo} class="flex flex-col gap-3">
			<label for="youtube-url-input" class="text-xs font-semibold uppercase tracking-wider text-tubi-muted">
				Tautan Video YouTube
			</label>
			<div class="flex flex-col sm:flex-row gap-2">
				<div class="relative flex-1">
					<input
						id="youtube-url-input"
						type="url"
						placeholder="Contoh: https://www.youtube.com/watch?v=..."
						bind:value={inputUrl}
						class="w-full bg-tubi-elevated border border-tubi-border rounded-lg px-4 py-3 text-sm text-tubi-text placeholder-tubi-muted/60 focus:border-tubi-accent focus:ring-1 focus:ring-tubi-accent transition-colors"
						autocomplete="off"
						spellcheck="false"
					/>
					{#if inputUrl}
						<button
							type="button"
							on:click={handleClear}
							aria-label="Hapus tautan input"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-tubi-muted hover:text-white px-1.5 py-1 rounded bg-tubi-border/40 hover:bg-tubi-border transition-colors"
						>
							Batal
						</button>
					{/if}
				</div>

				<div class="flex gap-2">
					<button
						type="button"
						on:click={handlePaste}
						class="px-4 py-3 text-xs font-medium bg-tubi-elevated hover:bg-tubi-border/80 border border-tubi-border text-tubi-text rounded-lg transition-colors flex items-center justify-center gap-1.5"
						title="Tempel dari Clipboard"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-tubi-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>
							<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
						</svg>
						<span>Tempel</span>
					</button>

					<button
						type="submit"
						disabled={isLoading || !inputUrl.trim()}
						class="flex-1 sm:flex-none px-6 py-3 text-sm font-semibold bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
					>
						{#if isLoading}
							<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>Menganalisis...</span>
						{:else}
							<span>Ambil Info</span>
						{/if}
					</button>
				</div>
			</div>
		</form>
	</section>

	<!-- Feedback Alerts -->
	{#if errorMessage}
		<div role="alert" class="bg-red-950/40 border border-red-800/60 rounded-xl p-4 text-sm text-red-200 flex items-start justify-between gap-3">
			<div class="flex items-start gap-2.5">
				<svg class="w-5 h-5 text-red-400 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10"/>
					<line x1="12" y1="8" x2="12" y2="12"/>
					<line x1="12" y1="16" x2="12.01" y2="16"/>
				</svg>
				<p class="leading-relaxed">{errorMessage}</p>
			</div>
			<button
				type="button"
				on:click={() => (errorMessage = '')}
				class="text-xs text-red-400 hover:text-red-200 underline shrink-0 mt-0.5"
			>
				Tutup
			</button>
		</div>
	{/if}

	{#if downloadSuccessMessage}
		<div role="status" class="bg-emerald-950/40 border border-emerald-800/60 rounded-xl p-4 text-sm text-emerald-200 flex items-center justify-between gap-3">
			<div class="flex items-center gap-2.5">
				<svg class="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<p>{downloadSuccessMessage}</p>
			</div>
			<button
				type="button"
				on:click={() => (downloadSuccessMessage = '')}
				class="text-xs text-emerald-400 hover:text-emerald-200 underline"
			>
				Tutup
			</button>
		</div>
	{/if}

	<!-- Result View -->
	{#if videoData}
		<section aria-label="Informasi dan Opsi Unduhan Video" class="bg-tubi-card border border-tubi-border rounded-xl p-5 md:p-6 flex flex-col gap-6">
			<!-- Video Header Info Card -->
			<div class="flex flex-col md:flex-row gap-5 items-start">
				<!-- Thumbnail Container with 16:9 Aspect Ratio -->
				<div class="relative w-full md:w-72 aspect-video bg-tubi-elevated rounded-lg overflow-hidden border border-tubi-border shrink-0">
					{#if videoData.thumbnail}
						<img
							src={videoData.thumbnail}
							alt="Thumbnail video: {videoData.title}"
							class="w-full h-full object-cover"
							loading="lazy"
						/>
					{:else}
						<div class="w-full h-full flex items-center justify-center text-xs text-tubi-muted">
							Thumbnail tidak tersedia
						</div>
					{/if}
					<div class="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/80 text-white text-xs font-mono font-medium backdrop-blur-sm">
						{videoData.duration_formatted}
					</div>
				</div>

				<!-- Video Details -->
				<div class="flex-1 flex flex-col justify-between gap-3">
					<div class="space-y-1.5">
						<h2 class="text-base md:text-lg font-semibold text-white leading-snug line-clamp-2">
							{videoData.title}
						</h2>
						<p class="text-xs md:text-sm text-tubi-muted flex items-center gap-2">
							<span class="font-medium text-tubi-text">{videoData.uploader}</span>
							<span>•</span>
							<span>{formatViews(videoData.view_count)}</span>
						</p>
					</div>

					<div class="pt-2 flex items-center gap-2">
						<a
							href={videoData.url}
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex items-center gap-1.5 text-xs text-tubi-muted hover:text-white transition-colors"
						>
							<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
								<polyline points="15 3 21 3 21 9"/>
								<line x1="10" y1="14" x2="21" y2="3"/>
							</svg>
							<span>Buka di YouTube</span>
						</a>
					</div>
				</div>
			</div>

			<!-- Tabs Format Selection -->
			<div class="border-t border-tubi-border pt-6 flex flex-col gap-4">
				<div class="flex border-b border-tubi-border gap-2" role="tablist">
					<button
						type="button"
						role="tab"
						aria-selected={activeTab === 'video'}
						on:click={() => (activeTab = 'video')}
						class="pb-2.5 px-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 {activeTab === 'video' ? 'border-tubi-accent text-white' : 'border-transparent text-tubi-muted hover:text-white'}"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<polygon points="23 7 16 12 23 17 23 7"/>
							<rect width="15" height="14" x="1" y="5" rx="2" ry="2"/>
						</svg>
						<span>Video (MP4)</span>
					</button>

					<button
						type="button"
						role="tab"
						aria-selected={activeTab === 'audio'}
						on:click={() => (activeTab = 'audio')}
						class="pb-2.5 px-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 {activeTab === 'audio' ? 'border-tubi-accent text-white' : 'border-transparent text-tubi-muted hover:text-white'}"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M9 18V5l12-2v13"/>
							<circle cx="6" cy="18" r="3"/>
							<circle cx="18" cy="16" r="3"/>
						</svg>
						<span>Audio (MP3)</span>
					</button>
				</div>

				<!-- Tab Content: Video MP4 -->
				{#if activeTab === 'video'}
					<div class="flex flex-col gap-2.5">
						{#each videoData.video_formats as item}
							<div class="flex items-center justify-between p-3.5 bg-tubi-elevated border border-tubi-border rounded-lg hover:border-tubi-border/80 transition-colors">
								<div class="flex items-center gap-3">
									<span class="px-2.5 py-1 text-xs font-semibold rounded bg-tubi-card border border-tubi-border text-white">
										{item.quality}
									</span>
									<span class="text-xs text-tubi-muted">
										Format MP4 • {item.label}
									</span>
								</div>

								<button
									type="button"
									disabled={downloadingKey !== null}
									on:click={() => triggerDownload('video', item.quality)}
									class="px-4 py-2 text-xs font-medium bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center gap-2"
								>
									{#if downloadingKey === `video-${item.quality}`}
										<svg class="animate-spin h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										<span>Menyiapkan...</span>
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
											<polyline points="7 10 12 15 17 10"/>
											<line x1="12" y1="15" x2="12" y2="3"/>
										</svg>
										<span>Unduh MP4</span>
									{/if}
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Tab Content: Audio MP3 -->
				{#if activeTab === 'audio'}
					<div class="flex flex-col gap-2.5">
						{#each videoData.audio_formats as item}
							<div class="flex items-center justify-between p-3.5 bg-tubi-elevated border border-tubi-border rounded-lg hover:border-tubi-border/80 transition-colors">
								<div class="flex items-center gap-3">
									<span class="px-2.5 py-1 text-xs font-semibold rounded bg-tubi-card border border-tubi-border text-white">
										{item.bitrate}
									</span>
									<span class="text-xs text-tubi-muted">
										Format Audio MP3 • {item.label}
									</span>
								</div>

								<button
									type="button"
									disabled={downloadingKey !== null}
									on:click={() => triggerDownload('audio', item.quality)}
									class="px-4 py-2 text-xs font-medium bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center gap-2"
								>
									{#if downloadingKey === `audio-${item.quality}`}
										<svg class="animate-spin h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
											<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
											<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
										</svg>
										<span>Mengonversi...</span>
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
											<polyline points="7 10 12 15 17 10"/>
											<line x1="12" y1="15" x2="12" y2="3"/>
										</svg>
										<span>Unduh MP3</span>
									{/if}
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</section>
	{:else if !isLoading}
		<!-- Empty State (R-27) -->
		<section aria-label="Panduan Penggunaan" class="border border-dashed border-tubi-border rounded-xl p-8 text-center space-y-2">
			<div class="w-10 h-10 rounded-full bg-tubi-elevated border border-tubi-border flex items-center justify-center mx-auto text-tubi-muted">
				<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
					<path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
				</svg>
			</div>
			<p class="text-sm font-medium text-tubi-text">Belum ada video yang dianalisis</p>
			<p class="text-xs text-tubi-muted max-w-md mx-auto">
				Salin URL video YouTube dari browser atau aplikasi, lalu tempelkan pada kolom di atas untuk melihat pilihan resolusi.
			</p>
		</section>
	{/if}
</main>

<!-- Footer -->
<footer class="border-t border-tubi-border py-6 bg-tubi-card/30 text-xs text-tubi-muted">
	<div class="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
		<p>Tubi: Alat bantu utilitas media pribadi berbasis SvelteKit dan FastAPI.</p>
		<p class="text-[11px] text-tubi-muted/80">Harap hormati hak cipta dan ketentuan layanan kreator video.</p>
	</div>
</footer>
