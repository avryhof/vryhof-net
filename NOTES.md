<nav class="navbar navbar-custom navbar-fixed-top">
    <div class="container">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#"><i class="fa fa-home"></i></a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
            <ul class="nav navbar-nav">
                <li><a href="#"><?= $weather->name; ?>, <?= $location['region']; ?></a></li>
                <li><a href="<?= $proto; ?>//facebook.com/" target="_blank"><i class="fa fa-facebook-official"></i></a></li>
                <li><a href="<?= $proto; ?>//www.linkedin.com/" target="_blank"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
                <li><a href="<?= $proto; ?>//www.amazon.com/" target="_blank"><i class="fa fa-amazon"></i></a></li>
                <li><a href="<?= $proto; ?>//www.dropbox.com/" target="_blank"><i class="fa fa-dropbox"></i></a></li>
                <li><a href="<?= $proto; ?>//webmail.vryhofresearch.com/" target="_blank" title="vryhof.net"><i
                            class="fa fa-envelope" aria-hidden="true"></i> Vryhof.NET</a></li>
                <li><a href="<?= $proto; ?>//gmail.vryhofresearch.com/" target="_blank" title="vryhofresearch.com"><i
                            class="fa fa-envelope" aria-hidden="true"></i> VryhofResearch.com</a></li>

            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li>
                    <a href="https://mail.google.com/mail/?tab=wm<?= ($providers['Google']['loggedin'] ? '&authuser=0' : ''); ?>">Gmail</a>
                </li>
                <li><a href="https://calendar.google.com/" target="_blank">Calendar</a></li>
                <li><a href="https://www.google.com/imghp" target="_blank">Images</a></li>
                <li><a href="https://news.google.com/" target="_blank">News</a></li>
            </ul>
        </div><!--/.nav-collapse -->
    </div>
</nav>
