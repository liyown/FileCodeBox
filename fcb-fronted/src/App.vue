<script setup lang="ts">
import Navigation from "@/components/Navigation.vue";

</script>

<template>

  <div>
    <Navigation class="nagivation" />
    <RouterView class="main"/>
  </div>
</template>

<style scoped>

a {
  color: #007bff; /* 设置链接颜色为蓝色 */
  text-decoration: none; /* 去除下划线 */
  font-size: 14px; /* 设置字体大小 */
  margin-right: 20px; /* 设置右边距 */
  white-space: nowrap;
  
}
/* 当鼠标悬停在链接上时，改变颜色 */
a:hover {
  color: #0056b3; /* 设置链接悬停时的颜色 */
}

.nagivation {
  background-color: #f8f9fa; /* 设置背景颜色 */
}

.main {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  display: flex;
}
</style>
