<?php
/**
 * Page templates.
 *
 * Two templates are offered in the page editor's Template dropdown. A page
 * that is not assigned one of them is never touched, which is what keeps the
 * rest of the site out of this.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Template slug to file.
 *
 * @return array
 */
function ke_templates() {
	return array(
		KNACK_TPL_SALES    => array(
			'label' => __( 'Knack Extra sales page', 'knack-extra' ),
			'file'  => 'templates/sales.php',
		),
		KNACK_TPL_POLICIES => array(
			'label' => __( 'Knack Extra policies', 'knack-extra' ),
			'file'  => 'templates/policies.php',
		),
	);
}

/**
 * Offer the templates in the page editor.
 *
 * @param array $templates Existing templates.
 * @return array
 */
function ke_register_templates( $templates ) {
	foreach ( ke_templates() as $slug => $tpl ) {
		$templates[ $slug ] = $tpl['label'];
	}
	return $templates;
}
add_filter( 'theme_page_templates', 'ke_register_templates' );

/**
 * Which of our templates, if any, is this request using?
 *
 * @return string Template slug, or '' when this is somebody else's page.
 */
function ke_current_template() {
	if ( ! is_page() ) {
		return '';
	}
	$slug = get_page_template_slug( get_queried_object_id() );
	return isset( ke_templates()[ $slug ] ) ? $slug : '';
}

/**
 * Is this request one of ours?
 *
 * @return bool
 */
function ke_is_ours() {
	return '' !== ke_current_template();
}

/**
 * Serve our file instead of the theme's.
 *
 * Priority 99 so that this runs after page builders have had their say. A
 * page built with Elementor will not be assigned one of our templates, so the
 * two never collide.
 *
 * @param string $template The template the theme chose.
 * @return string
 */
function ke_template_include( $template ) {
	$slug = ke_current_template();
	if ( '' === $slug ) {
		return $template;
	}
	$file = KNACK_DIR . ke_templates()[ $slug ]['file'];
	return file_exists( $file ) ? $file : $template;
}
add_filter( 'template_include', 'ke_template_include', 99 );

/**
 * Permalink of the page using one of our templates.
 *
 * Looked up by template rather than by slug, so the pages can be called
 * whatever you like and can sit anywhere in the site, for example at
 * /knackextra/ with the policies page as its child.
 *
 * @param string $template One of the KNACK_TPL_* slugs.
 * @return string Empty when no published page uses that template.
 */
function ke_page_url( $template ) {
	$key    = 'ke_url_' . $template;
	$cached = get_transient( $key );
	if ( is_string( $cached ) ) {
		return $cached;
	}

	$pages = get_posts(
		array(
			'post_type'        => 'page',
			'post_status'      => 'publish',
			'posts_per_page'   => 1,
			'fields'           => 'ids',
			'orderby'          => 'ID',
			'order'            => 'ASC',
			'suppress_filters' => false,
			'meta_key'         => '_wp_page_template',
			'meta_value'       => $template,
		)
	);

	$url = $pages ? (string) get_permalink( $pages[0] ) : '';
	set_transient( $key, $url, DAY_IN_SECONDS );
	return $url;
}

/**
 * Permalink of the policies page.
 *
 * @return string
 */
function ke_policies_url() {
	return ke_page_url( KNACK_TPL_POLICIES );
}

/**
 * Permalink of the sales page.
 *
 * @return string
 */
function ke_sales_url() {
	return ke_page_url( KNACK_TPL_SALES );
}

/**
 * The lookups above are cached, so forget them whenever a page changes.
 */
function ke_forget_urls() {
	delete_transient( 'ke_url_' . KNACK_TPL_SALES );
	delete_transient( 'ke_url_' . KNACK_TPL_POLICIES );
}
add_action( 'save_post_page', 'ke_forget_urls' );
add_action( 'deleted_post', 'ke_forget_urls' );
add_action( 'switch_theme', 'ke_forget_urls' );
