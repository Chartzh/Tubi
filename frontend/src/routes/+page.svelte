<script>
	import { onMount } from 'svelte';
	import { env } from '$env/dynamic/public';

	const API_BASE = (env.PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

	let inputUrl = '';
	let isLoading = false;
	let errorMessage = '';
	let videoData = null;
	let activeTab = 'video'; // 'video' | 'audio'
	let selectedVideoQuality = '';
	let selectedAudioQuality = '320k';
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
			// Default selection to the highest available video format
			if (data.video_formats && data.video_formats.length > 0) {
				selectedVideoQuality = data.video_formats[0].quality;
			}
			if (data.audio_formats && data.audio_formats.length > 0) {
				selectedAudioQuality = data.audio_formats[0].quality;
			}
		} catch (err) {
			errorMessage = err.message || 'Tidak dapat terhubung ke server backend Tubi.';
		} finally {
			isLoading = false;
		}
	}

	function triggerDownload(type, quality) {
		if (!videoData) return;

		const targetQuality = quality || (type === 'video' ? selectedVideoQuality : selectedAudioQuality);
		const key = `${type}-${targetQuality}`;
		downloadingKey = key;
		downloadSuccessMessage = '';

		const params = new URLSearchParams({
			url: videoData.url,
			type: type,
			quality: targetQuality,
			title: videoData.title
		});

		const downloadUrl = `${API_BASE}/api/download?${params.toString()}`;

		// Trigger download via anchor tag
		const a = document.createElement('a');
		a.href = downloadUrl;
		a.setAttribute('download', '');
		a.style.display = 'none';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		setTimeout(() => {
			downloadingKey = null;
			downloadSuccessMessage = `Permintaan unduhan ${type.toUpperCase()} (${targetQuality}) telah dikirim ke browser.`;
		}, 2000);
	}

	function handleKeydown(event) {
		if (event.key === 'Escape') {
			handleClear();
		}
	}

	function formatViews(count) {
		if (!count && count !== 0) return 'Tayangan tidak diketahui';
		if (count >= 1000000) {
			return `${(count / 1000000).toFixed(1)} jt tayangan`;
		}
		if (count >= 1000) {
			return `${(count / 1000).toFixed(1)} rb tayangan`;
		}
		return `${count} tayangan`;
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<svelte:head>
	<title>Tubi: YouTube Media Converter Deck</title>
</svelte:head>

<!-- Top Header Navigation -->
<header class="border-b border-tubi-border bg-tubi-card/80 backdrop-blur-md sticky top-0 z-20">
	<div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
		<!-- Brand Logo -->
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-lg bg-tubi-accent flex items-center justify-center text-white font-display font-bold text-base shadow-sm">
				T
			</div>
			<div class="flex items-center gap-2">
				<span class="font-display font-bold text-lg tracking-tight text-white">Tubi</span>
				<span class="text-[11px] font-mono text-tubi-muted px-2 py-0.5 rounded bg-tubi-elevated border border-tubi-border">CORE V2.4</span>
			</div>
		</div>

		<!-- Status Indicator -->
		<div class="flex items-center gap-2 text-xs font-mono text-tubi-muted">
			<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
			<span>Layanan Aktif</span>
		</div>
	</div>
</header>

<!-- Main Container -->
<main class="flex-1 max-w-5xl w-full mx-auto px-4 py-8 md:py-12 flex flex-col gap-10">
	<!-- Hero Section -->
	<section class="text-center space-y-3 max-w-2xl mx-auto">
		<h1 class="text-3xl md:text-5xl font-display font-bold tracking-tight text-white leading-tight">
			Ekstraksi Media YouTube, <span class="text-tubi-accent">Presisi & Bersih.</span>
		</h1>
		<p class="text-sm md:text-base text-tubi-muted leading-relaxed">
			Unduh video format MP4 resolusi hingga 1080p atau audio MP3 jernih langsung ke perangkat Anda tanpa iklan atau tautan pengalih.
		</p>
		<div class="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs font-mono text-tubi-muted">
			<span class="px-2.5 py-1 rounded bg-tubi-elevated/70 border border-tubi-border">YouTube Video</span>
			<span class="px-2.5 py-1 rounded bg-tubi-elevated/70 border border-tubi-border">YouTube Shorts</span>
			<span class="px-2.5 py-1 rounded bg-tubi-elevated/70 border border-tubi-border">YouTube Music</span>
		</div>
	</section>

	<!-- Converter Deck Card -->
	<section aria-label="Deck Konverter Media" class="bg-tubi-deck border border-tubi-border rounded-2xl p-5 md:p-8 shadow-2xl flex flex-col gap-6">
		<!-- Deck Input Bar -->
		<form on:submit|preventDefault={fetchVideoInfo} class="flex flex-col gap-2">
			<label for="youtube-url-input" class="text-xs font-mono uppercase tracking-wider text-tubi-muted flex items-center justify-between">
				<span>Tautan Video YouTube</span>
				<span class="text-[11px] text-tubi-muted/70 lowercase font-sans">Tekan Enter untuk memproses</span>
			</label>
			<div class="flex flex-col sm:flex-row gap-2.5">
				<div class="relative flex-1">
					<div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-tubi-accent pointer-events-none">
						<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
							<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
						</svg>
					</div>
					<input
						id="youtube-url-input"
						type="url"
						placeholder="https://www.youtube.com/watch?v=..."
						bind:value={inputUrl}
						class="w-full bg-tubi-elevated border border-tubi-border rounded-xl pl-10 pr-16 py-3.5 text-sm text-tubi-text placeholder-tubi-muted/50 focus:border-tubi-accent focus:ring-1 focus:ring-tubi-accent transition-colors font-sans"
						autocomplete="off"
						spellcheck="false"
					/>
					{#if inputUrl}
						<button
							type="button"
							on:click={handleClear}
							aria-label="Hapus tautan input"
							class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-tubi-muted hover:text-white px-2 py-1 rounded-lg bg-tubi-border/50 hover:bg-tubi-border transition-colors"
						>
							Batal
						</button>
					{/if}
				</div>

				<div class="flex gap-2">
					<button
						type="button"
						on:click={handlePaste}
						class="px-4 py-3.5 text-xs font-mono bg-tubi-elevated hover:bg-tubi-border border border-tubi-border text-tubi-text rounded-xl transition-colors flex items-center justify-center gap-1.5"
						title="Tempel dari Clipboard (Ctrl+V)"
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
						class="flex-1 sm:flex-none px-6 py-3.5 text-xs font-display font-semibold uppercase tracking-wider bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
					>
						{#if isLoading}
							<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>Menganalisis...</span>
						{:else}
							<span>Ambil Media</span>
						{/if}
					</button>
				</div>
			</div>
		</form>

		<!-- Feedback Alerts -->
		{#if errorMessage}
			<div role="alert" class="bg-red-950/40 border border-red-800/60 rounded-xl p-4 text-xs md:text-sm text-red-200 flex items-start justify-between gap-3">
				<div class="flex items-start gap-2.5">
					<svg class="w-4 h-4 text-red-400 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="10"/>
						<line x1="12" y1="8" x2="12" y2="12"/>
						<line x1="12" y1="16" x2="12.01" y2="16"/>
					</svg>
					<p class="leading-relaxed">{errorMessage}</p>
				</div>
				<button
					type="button"
					on:click={() => (errorMessage = '')}
					class="text-xs text-red-400 hover:text-red-200 underline shrink-0"
				>
					Tutup
				</button>
			</div>
		{/if}

		{#if downloadSuccessMessage}
			<div role="status" class="bg-emerald-950/40 border border-emerald-800/60 rounded-xl p-4 text-xs md:text-sm text-emerald-200 flex items-center justify-between gap-3">
				<div class="flex items-center gap-2.5">
					<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
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

		<!-- Result State: Cyber-Arcade Converter Deck Content -->
		{#if videoData}
			<div class="border-t border-tubi-border pt-6 flex flex-col lg:flex-row gap-8 items-start">
				<!-- Left Column: Video Preview & Details -->
				<div class="w-full lg:w-5/12 flex flex-col gap-4">
					<!-- Thumbnail Container -->
					<div class="relative w-full aspect-video bg-tubi-elevated rounded-xl overflow-hidden border border-tubi-border shadow-md group">
						{#if videoData.thumbnail}
							<img
								src={videoData.thumbnail}
								alt="Thumbnail: {videoData.title}"
								class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
								loading="lazy"
							/>
						{:else}
							<div class="w-full h-full flex items-center justify-center text-xs text-tubi-muted">
								Thumbnail tidak tersedia
							</div>
						{/if}
						<div class="absolute bottom-2.5 right-2.5 px-2 py-0.5 rounded-md bg-black/85 text-white text-xs font-mono font-medium backdrop-blur-sm border border-white/10">
							{videoData.duration_formatted}
						</div>
					</div>

					<!-- Video Metadata -->
					<div class="space-y-2 bg-tubi-elevated/40 border border-tubi-border/70 rounded-xl p-4">
						<h2 class="text-base font-display font-bold text-white leading-snug line-clamp-2">
							{videoData.title}
						</h2>
						<div class="flex items-center justify-between text-xs text-tubi-muted pt-1">
							<span class="font-medium text-tubi-text truncate max-w-[180px]">{videoData.uploader}</span>
							<span class="font-mono">{formatViews(videoData.view_count)}</span>
						</div>
						<div class="pt-2 border-t border-tubi-border/40 flex items-center justify-between">
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
							<button
								type="button"
								on:click={handleClear}
								class="text-xs text-tubi-muted hover:text-tubi-accent transition-colors"
							>
								Ganti Video
							</button>
						</div>
					</div>
				</div>

				<!-- Right Column: Format Deck & Download Action -->
				<div class="w-full lg:w-7/12 flex flex-col gap-5">
					<!-- Format Switcher Tabs -->
					<div class="flex border-b border-tubi-border gap-2" role="tablist">
						<button
							type="button"
							role="tab"
							aria-selected={activeTab === 'video'}
							on:click={() => (activeTab = 'video')}
							class="pb-3 px-4 text-xs font-display font-semibold uppercase tracking-wider border-b-2 transition-all flex items-center gap-2 {activeTab === 'video' ? 'border-tubi-accent text-white' : 'border-transparent text-tubi-muted hover:text-white'}"
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
							class="pb-3 px-4 text-xs font-display font-semibold uppercase tracking-wider border-b-2 transition-all flex items-center gap-2 {activeTab === 'audio' ? 'border-tubi-accent text-white' : 'border-transparent text-tubi-muted hover:text-white'}"
						>
							<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M9 18V5l12-2v13"/>
								<circle cx="6" cy="18" r="3"/>
								<circle cx="18" cy="16" r="3"/>
							</svg>
							<span>Audio (MP3)</span>
						</button>
					</div>

					<!-- Quality Options Grid -->
					{#if activeTab === 'video'}
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-3" role="radiogroup" aria-label="Pilihan Kualitas Video">
							{#each videoData.video_formats as item}
								<button
									type="button"
									role="radio"
									aria-checked={selectedVideoQuality === item.quality}
									on:click={() => (selectedVideoQuality = item.quality)}
									class="p-4 rounded-xl border text-left transition-all flex flex-col justify-between gap-3 {selectedVideoQuality === item.quality ? 'border-tubi-accent bg-tubi-accent/10 ring-1 ring-tubi-accent' : 'border-tubi-border bg-tubi-elevated/60 hover:border-tubi-border-focus'}"
								>
									<div class="flex items-center justify-between">
										<span class="font-display font-bold text-base text-white">{item.quality}</span>
										<span class="px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider rounded bg-tubi-deck border border-tubi-border text-tubi-muted">
											{item.label}
										</span>
									</div>
									<div class="flex items-center justify-between text-xs text-tubi-muted">
										<span>Format MP4</span>
										{#if selectedVideoQuality === item.quality}
											<span class="text-tubi-accent font-mono text-[11px] font-semibold">Dipilih</span>
										{/if}
									</div>
								</button>
							{/each}
						</div>

						<!-- Primary Download Button for Video -->
						<div class="pt-2">
							<button
								type="button"
								disabled={downloadingKey !== null}
								on:click={() => triggerDownload('video', selectedVideoQuality)}
								class="w-full py-4 px-6 text-sm font-display font-bold uppercase tracking-wider bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-md flex items-center justify-center gap-2.5"
							>
								{#if downloadingKey === `video-${selectedVideoQuality}`}
									<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
									<span>Menyiapkan Berkas Video...</span>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
										<polyline points="7 10 12 15 17 10"/>
										<line x1="12" y1="15" x2="12" y2="3"/>
									</svg>
									<span>Unduh Video ({selectedVideoQuality || 'MP4'})</span>
								{/if}
							</button>
						</div>
					{/if}

					{#if activeTab === 'audio'}
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-3" role="radiogroup" aria-label="Pilihan Kualitas Audio">
							{#each videoData.audio_formats as item}
								<button
									type="button"
									role="radio"
									aria-checked={selectedAudioQuality === item.quality}
									on:click={() => (selectedAudioQuality = item.quality)}
									class="p-4 rounded-xl border text-left transition-all flex flex-col justify-between gap-3 {selectedAudioQuality === item.quality ? 'border-tubi-accent bg-tubi-accent/10 ring-1 ring-tubi-accent' : 'border-tubi-border bg-tubi-elevated/60 hover:border-tubi-border-focus'}"
								>
									<div class="flex items-center justify-between">
										<span class="font-display font-bold text-base text-white">{item.bitrate}</span>
										<span class="px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider rounded bg-tubi-deck border border-tubi-border text-tubi-muted">
											{item.label}
										</span>
									</div>
									<div class="flex items-center justify-between text-xs text-tubi-muted">
										<span>Format MP3</span>
										{#if selectedAudioQuality === item.quality}
											<span class="text-tubi-accent font-mono text-[11px] font-semibold">Dipilih</span>
										{/if}
									</div>
								</button>
							{/each}
						</div>

						<!-- Primary Download Button for Audio -->
						<div class="pt-2">
							<button
								type="button"
								disabled={downloadingKey !== null}
								on:click={() => triggerDownload('audio', selectedAudioQuality)}
								class="w-full py-4 px-6 text-sm font-display font-bold uppercase tracking-wider bg-tubi-accent hover:bg-tubi-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-md flex items-center justify-center gap-2.5"
							>
								{#if downloadingKey === `audio-${selectedAudioQuality}`}
									<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
									<span>Mengonversi Berkas Audio...</span>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
										<polyline points="7 10 12 15 17 10"/>
										<line x1="12" y1="15" x2="12" y2="3"/>
									</svg>
									<span>Unduh Audio MP3 ({selectedAudioQuality})</span>
								{/if}
							</button>
						</div>
					{/if}
				</div>
			</div>
		{:else if !isLoading}
			<!-- Empty State (R-27) -->
			<div class="border border-dashed border-tubi-border rounded-xl p-8 text-center space-y-3 bg-tubi-elevated/20">
				<div class="w-10 h-10 rounded-full bg-tubi-elevated border border-tubi-border flex items-center justify-center mx-auto text-tubi-muted">
					<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-tubi-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
						<path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
					</svg>
				</div>
				<div class="space-y-1">
					<p class="text-sm font-display font-medium text-tubi-text">Deck Siap: Belum ada video yang dimuat</p>
					<p class="text-xs text-tubi-muted max-w-md mx-auto">
						Tempelkan tautan YouTube di atas untuk memilih format unduhan video atau ekstraksi audio MP3.
					</p>
				</div>
			</div>
		{/if}

		<!-- Deck Bottom Status Line -->
		<div class="border-t border-tubi-border/60 pt-4 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-tubi-muted gap-2">
			<div class="flex items-center gap-4">
				<span><kbd class="px-1.5 py-0.5 rounded bg-tubi-elevated border border-tubi-border">Enter</kbd> Proses</span>
				<span><kbd class="px-1.5 py-0.5 rounded bg-tubi-elevated border border-tubi-border">Esc</kbd> Reset</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="w-1.5 h-1.5 rounded-full bg-tubi-cyan"></span>
				<span>Output MP4 & MP3 Langsung</span>
			</div>
		</div>
	</section>

	<!-- Honest Feature Highlights (R-36, R-38) -->
	<section aria-label="Keunggulan Tubi" class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<div class="bg-tubi-card border border-tubi-border rounded-xl p-5 space-y-2">
			<div class="w-8 h-8 rounded-lg bg-tubi-elevated border border-tubi-border flex items-center justify-center text-tubi-accent">
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<rect width="20" height="14" x="2" y="3" rx="2"/>
					<line x1="8" y1="21" x2="16" y2="21"/>
					<line x1="12" y1="17" x2="12" y2="21"/>
				</svg>
			</div>
			<h3 class="font-display font-semibold text-sm text-white">Kualitas Orisinal</h3>
			<p class="text-xs text-tubi-muted leading-relaxed">
				Mengunduh langsung stream terbaik YouTube tanpa re-encoding sekunder yang menurunkan resolusi atau ketajaman visual.
			</p>
		</div>

		<div class="bg-tubi-card border border-tubi-border rounded-xl p-5 space-y-2">
			<div class="w-8 h-8 rounded-lg bg-tubi-elevated border border-tubi-border flex items-center justify-center text-tubi-accent">
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
				</svg>
			</div>
			<h3 class="font-display font-semibold text-sm text-white">Bebas Iklan & Pelacak</h3>
			<p class="text-xs text-tubi-muted leading-relaxed">
				Antarmuka bersih tanpa pop-up berbahaya, tautan pengalih (redirect), atau injeksi skrip pelacak pihak ketiga.
			</p>
		</div>

		<div class="bg-tubi-card border border-tubi-border rounded-xl p-5 space-y-2">
			<div class="w-8 h-8 rounded-lg bg-tubi-elevated border border-tubi-border flex items-center justify-center text-tubi-accent">
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M9 18V5l12-2v13"/>
					<circle cx="6" cy="18" r="3"/>
					<circle cx="18" cy="16" r="3"/>
				</svg>
			</div>
			<h3 class="font-display font-semibold text-sm text-white">Ekstraksi Audio Cepat</h3>
			<p class="text-xs text-tubi-muted leading-relaxed">
				Mengekstrak trek audio langsung ke format MP3 berkecepatan tinggi dengan bit-rate hingga 320 kbps.
			</p>
		</div>
	</section>
</main>

<!-- Footer -->
<footer class="border-t border-tubi-border py-6 bg-tubi-card/30 text-xs text-tubi-muted">
	<div class="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
		<p>Tubi: Utilitas pengunduh media YouTube lokal berbasis SvelteKit dan FastAPI.</p>
		<p class="text-[11px] text-tubi-muted/80">Gunakan secara bertanggung jawab sesuai hak cipta kreator.</p>
	</div>
</footer>
