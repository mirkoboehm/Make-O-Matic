<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  xmlns="http://www.w3.org/1999/xhtml">

  <xsl:output method="text" indent="no" encoding="UTF-8"/>
  
  <xsl:strip-space elements="*"/>

<xsl:template match="build">
/
| BUILD REPORT
|    
| Build Report for: <xsl:value-of select="@name"/>
\
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="project">
/
| Project: <xsl:value-of select="@name"/>
|
| Base directory: <xsl:value-of select="@basedir"/>
|
| Start time (UTC): <xsl:value-of select="@starttime"/>
| End time (UTC): <xsl:value-of select="@stoptime"/>
|
| Build time: <xsl:value-of select="@timing"/>
\
    <xsl:apply-templates/>
  </xsl:template>

<xsl:template match="environment">
% Environment: <xsl:value-of select="@name"/> %
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="configuration">
; Configuration: <xsl:value-of select="@name"/> ;
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="plugin">
# Plugin: <xsl:value-of select="@name"/> #
  <xsl:choose>
    <!-- Plugin templates are inserted here -->
    <xsl:when test="@name = 'placeholder'">
    </xsl:when>
    <xsl:otherwise>
      <xsl:if test="count(./*) > 0">
        <xsl:apply-templates/>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose> 
</xsl:template>

<xsl:template match="step">
  <xsl:choose>
    <xsl:when test="@failed = 'False'">
      <xsl:text>success: </xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>!failed! </xsl:text>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:text>Step "</xsl:text><xsl:value-of select="@name"/>" (took: <xsl:value-of select="@timing"/>)
  <xsl:if test="@failed = 'True'">
    <xsl:if test="count(./action) > 0">
      <xsl:apply-templates></xsl:apply-templates>
    </xsl:if>
  </xsl:if>
</xsl:template>

<xsl:template match="step/action">
  <xsl:choose>
    <xsl:when test="@returncode = 0">
      <xsl:text>  success:  </xsl:text>
    </xsl:when>
    <xsl:when test="number(@returncode)">
      <xsl:text>  !failed!  </xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>  disabled: </xsl:text>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:text>Action </xsl:text><xsl:value-of select="logdescription"/>
  <xsl:text> (took: </xsl:text><xsl:value-of select="@timing"/><xsl:text>)</xsl:text>

  <xsl:if test="number(@returncode) and @returncode != 0">
    <xsl:if test="string-length(stderr) > 0">

[ --------------------------------- stderr --------------------------------- [
<xsl:value-of select="stderr"/>
] --------------------------------- stderr --------------------------------- ]
    </xsl:if>
<xsl:if test="string-length(stdout) > 0">

[[[ ------------------------------- stdout ------------------------------- [[[
    <xsl:value-of select="stdout"/>
]]] ------------------------------- stdout ------------------------------- ]]]
    </xsl:if>
  </xsl:if>
  
  <xsl:text>
  </xsl:text>
</xsl:template>

</xsl:stylesheet>
