<?php
/**
 * Fallback template.
 *
 * This is a single page sales site. Anything that is not the front page or a
 * page gets the plain document layout rather than a blog archive.
 *
 * @package knack-extra
 */

get_header();
?>
<main class="band on-light" id="main" style="background:var(--ivory)">
  <div class="wrap">
    <div class="doc">
	<?php
	if ( have_posts() ) {
		while ( have_posts() ) {
			the_post();
			echo '<h1 class="display">' . esc_html( get_the_title() ) . '</h1>';
			the_content();
		}
	} else {
		echo '<h1 class="display">Nothing here</h1>';
		echo '<p>That page could not be found.</p>';
	}
	?>
      <p style="margin-top:2.5rem">
        <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="btn btn-dark">Back to the website</a>
      </p>
    </div>
  </div>
</main>
<?php
get_footer();
