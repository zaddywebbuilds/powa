<?php
/**
 * Asset paths, enqueueing, and keeping the active theme out of the way.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * URL of a file inside the plugin's assets folder.
 *
 * The templates are generated from the static build, where every path is
 * relative ("assets/img/hero-dark.webp"). This turns one of those into a
 * plugin URL, so the same markup serves both builds.
 *
 * @param string $path Path below assets/, with no leading slash.
 * @return string
 */
function ke_asset( $path ) {
	return KNACK_URL . 'assets/' . ltrim( $path, '/' );
}

/**
 * Cache busting version for an asset: the file's own modification time.
 *
 * A stale site.js paired with fresh markup is not cosmetic here. The hero
 * video has no `src` in the markup, so an old script means no video at all,
 * and the package thumbnails fall back to the full size art.
 *
 * @param string $path Path below assets/.
 * @return string
 */
function ke_ver( $path ) {
	$file = KNACK_DIR . 'assets/' . ltrim( $path, '/' );
	$time = file_exists( $file ) ? filemtime( $file ) : 0;
	return $time ? (string) $time : KNACK_VERSION;
}

/**
 * Paths handed to the front end. site.js falls back to relative paths when
 * this is absent, which is what happens on the static build.
 *
 * @return array
 */
function ke_paths() {
	return array(
		'assets'   => trailingslashit( KNACK_URL . 'assets' ),
		'policies' => ke_policies_url(),
		'home'     => get_permalink(),
	);
}

/**
 * Styles and scripts, on our pages only.
 */
function ke_enqueue() {
	if ( ! ke_is_ours() ) {
		return;
	}

	wp_enqueue_style( 'knack-site', ke_asset( 'css/site.css' ), array(), ke_ver( 'css/site.css' ) );
	wp_enqueue_style( 'knack-wp', ke_asset( 'css/wordpress.css' ), array( 'knack-site' ), ke_ver( 'css/wordpress.css' ) );

	if ( ke_has_order_form() ) {
		wp_enqueue_style( 'knack-fluentform', ke_asset( 'css/fluentform.css' ), array( 'knack-site' ), ke_ver( 'css/fluentform.css' ) );
	}

	wp_enqueue_script( 'knack-config', ke_asset( 'js/config.js' ), array(), ke_ver( 'js/config.js' ), false );
	wp_add_inline_script( 'knack-config', 'window.KNACK_PATHS = ' . wp_json_encode( ke_paths() ) . ';', 'before' );
	wp_enqueue_script( 'knack-site', ke_asset( 'js/site.js' ), array( 'knack-config' ), ke_ver( 'js/site.js' ), true );

	if ( KNACK_TPL_POLICIES === ke_current_template() ) {
		wp_enqueue_script( 'knack-policies', ke_asset( 'js/policies.js' ), array( 'knack-config' ), ke_ver( 'js/policies.js' ), true );
	}
}
add_action( 'wp_enqueue_scripts', 'ke_enqueue' );

/**
 * Drop the active theme's own stylesheets, on our pages only.
 *
 * These templates render a complete document with their own header, footer
 * and design system, the way a page builder's canvas template does. Whatever
 * the site's theme is, its stylesheet has opinions about body, headings,
 * buttons and links that would fight this page for no benefit. Every other
 * page on the site keeps the theme untouched.
 *
 * Only stylesheets served from the theme directory are removed, found by
 * their URL rather than by a guessed handle name, so this works whatever
 * theme is active. Filter `knack_dequeue_theme_styles` to false to keep them.
 */
function ke_drop_theme_styles() {
	if ( ! ke_is_ours() || ! apply_filters( 'knack_dequeue_theme_styles', true ) ) {
		return;
	}

	$roots = array_unique(
		array(
			trailingslashit( get_template_directory_uri() ),
			trailingslashit( get_stylesheet_directory_uri() ),
		)
	);

	$styles = wp_styles();
	foreach ( (array) $styles->queue as $handle ) {
		if ( empty( $styles->registered[ $handle ] ) ) {
			continue;
		}
		$src = (string) $styles->registered[ $handle ]->src;
		if ( '' === $src ) {
			continue;
		}
		foreach ( $roots as $root ) {
			if ( 0 === strpos( $src, $root ) ) {
				wp_dequeue_style( $handle );
				break;
			}
		}
	}
}
add_action( 'wp_enqueue_scripts', 'ke_drop_theme_styles', 100 );

/**
 * Preload the two fonts, and the hero poster on the sales page.
 */
function ke_preload() {
	if ( ! ke_is_ours() ) {
		return;
	}

	foreach ( array( 'fonts/manrope-400.woff2', 'fonts/playfair-500.woff2' ) as $font ) {
		printf(
			'<link rel="preload" as="font" type="font/woff2" href="%s" crossorigin>' . "\n",
			esc_url( ke_asset( $font ) )
		);
	}

	if ( KNACK_TPL_SALES === ke_current_template() ) {
		printf(
			'<link rel="preload" as="image" href="%s" fetchpriority="high">' . "\n",
			esc_url( ke_asset( 'img/hero-sprout-poster-480.webp' ) )
		);
	}
}
add_action( 'wp_head', 'ke_preload', 2 );
